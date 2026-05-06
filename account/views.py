from django.shortcuts import render, redirect
from django.views import View
from .models import Account
from datetime import datetime
from createevent.models import Document, Survey, Appointment, AppointmentSurvey
import pandas as pd
import os
import json


class HomeView(View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, self.template_name)


class RegisterUser(View):
    template_name = 'register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):

        dob_input = request.POST.get('dob')

        dob = None
        if dob_input:
            try:
                dob = datetime.strptime(dob_input, "%m/%d/%Y").date()
            except ValueError:
                dob = None

        Account.objects.create(
            username=request.POST.get('username'),
            password=request.POST.get('password'),
            fullname=request.POST.get('fullName'),
            email=request.POST.get('email'),
            dob=dob,
            address=request.POST.get('address'),
            phone=request.POST.get('phone'),
            type=request.POST.get('type')
        )

        request.session.flush()
        return redirect('loginUser')


class LoginUser(View):
    template_name = 'login.html'

    def get(self, request):
        username = request.session.get('username')

        if username:
            try:
                user = Account.objects.get(username=username)
                return render(request, self.template_name, {
                    'success': user.fullname,
                    'type': user.type
                })
            except Account.DoesNotExist:
                pass

        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Account.objects.get(
                username=username,
                password=password
            )

            request.session['username'] = user.username

            return render(request, self.template_name, {
                'success': user.fullname,
                'type': user.type
            })

        except Account.DoesNotExist:
            return render(request, self.template_name, {
                'error': 'Invalid username or password'
            })


class EditProfile(View):
    template_name = 'editProfile.html'

    def get(self, request):
        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        user = Account.objects.get(username=username)

        return render(request, self.template_name, {
            'user': user
        })

    def post(self, request):
        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        user = Account.objects.get(username=username)

        user.fullname = request.POST.get('fullName')
        user.email = request.POST.get('email')
        user.address = request.POST.get('address')
        user.phone = request.POST.get('phone')

        dob_input = request.POST.get('dob')
        if dob_input:
            try:
                user.dob = datetime.strptime(dob_input, "%m/%d/%Y").date()
            except ValueError:
                pass

        user.save()

        return redirect('loginUser')


class LogoutUser(View):
    def get(self, request):
        request.session.flush()   # clears session
        return redirect('loginUser')

class DocumentStatus(View):
    def get(self, request):
        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        user = Account.objects.get(username=username)

        documents = Document.objects.filter(user=user).order_by('-documentID')

        return render(request, 'document_status.html', {
            'documents': documents
        })

    def post(self, request):
        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        document_id = request.POST.get('id')

        try:
            user = Account.objects.get(username=username)

            document = Document.objects.get(
                documentID=document_id,
                user=user
            )

            if document.status == "Completed":
                document.delete()

        except Document.DoesNotExist:
            pass

        return redirect('documentStatus')



class RequestDocument(View):
    template_name = 'request_document.html'

    def get(self, request):

        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        return render(request, self.template_name)

    def post(self, request):
        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        try:
            user = Account.objects.get(username=username)

            agency = request.POST.get('agency')
            document_type = request.POST.get('document_type')
            purpose = request.POST.get('purpose')
            description = request.POST.get('description')

            Document.objects.create(
                user=user,
                agency=agency,
                document_type=document_type,
                purpose=purpose,
                description=description,
                status="Pending"   # default status
            )

            return redirect('documentStatus')

        except Account.DoesNotExist:
            return redirect('loginUser')

class UserAnalytics(View):
    template_name = 'employee.html'

    def get(self, request):

        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        status = request.GET.get('status')

        documents = Document.objects.filter(
            is_imported=False
        ).order_by('-documentID')

        if status:
            documents = documents.filter(status=status)

        return render(request, self.template_name, {
            'documents': documents
        })

    def post(self, request):

        doc_id = request.POST.get('id')
        action = request.POST.get('action')

        try:

            document = Document.objects.get(
                documentID=doc_id
            )

            if action == "processing":
                document.status = "Processing"

            elif action == "releasing":
                document.status = "For Releasing"

            elif action == "completed":
                document.status = "Completed"

            document.save()

        except Document.DoesNotExist:
            pass

        return redirect('userAnalytics')

class Dashboard(View):

    def get(self, request):

        file_path = os.path.join(
            'data',
            '311_Service_Requests_from_2010_to_Present.csv'
        )

        df = pd.read_csv(file_path)

        selected_agency = request.GET.get('agency')

        if selected_agency:
            df = df[df['Agency'] == selected_agency]

        status_counts = df['Status'].value_counts()

        status_labels = list(status_counts.index)

        # 🔥 FIXED int64 ERROR
        status_values = [
            int(x) for x in status_counts.values
        ]

        agency_counts = df['Agency'].value_counts().head(5)

        agency_labels = list(agency_counts.index)

        agency_values = [
            int(x) for x in agency_counts.values
        ]

        service_counts = (
            df['Complaint Type']
            .value_counts()
            .head(5)
        )

        service_labels = list(service_counts.index)

        service_values = [
            int(x) for x in service_counts.values
        ]

        borough_counts = (
            df['Borough']
            .value_counts()
            .head(5)
        )

        location_labels = list(borough_counts.index)

        location_values = [
            int(x) for x in borough_counts.values
        ]

        total_requests = int(len(df))

        top_agency = (
            agency_labels[0]
            if agency_labels else 'N/A'
        )

        top_service = (
            service_labels[0]
            if service_labels else 'N/A'
        )

        top_status = (
            status_labels[0]
            if status_labels else 'N/A'
        )

        return render(request, 'dashboard.html', {

            'status_labels': json.dumps(status_labels),
            'status_values': json.dumps(status_values),

            'agency_labels': json.dumps(agency_labels),
            'agency_values': json.dumps(agency_values),

            'service_labels': json.dumps(service_labels),
            'service_values': json.dumps(service_values),

            'location_labels': json.dumps(location_labels),
            'location_values': json.dumps(location_values),

            'total_requests': total_requests,

            'top_agency': top_agency,
            'top_service': top_service,
            'top_status': top_status,

            'selected_agency': selected_agency,
        })

class SubmitSurvey(View):
    template_name = 'survey.html'

    def get(self, request, document_id):
        try:
            document = Document.objects.get(documentID=document_id)
        except Document.DoesNotExist:
            return redirect('documentStatus')

        return render(request, self.template_name, {
            'document': document
        })

    def post(self, request, document_id):
        try:
            document = Document.objects.get(documentID=document_id)
        except Document.DoesNotExist:
            return redirect('documentStatus')

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Survey.objects.create(
            document=document,
            rating=rating,
            comment=comment
        )

        return redirect('documentStatus')

class HelpFAQ(View):
        template_name = 'help_faq.html'

        def get(self, request):
            username = request.session.get('username')

            if not username:
                return redirect('loginUser')

            documents = Document.objects.all()

            return render(request, self.template_name, {
                'documents': documents
            })

class BookAppointment(View):
    def get(self, request):
        return render(request, 'book_appointment.html')

    def post(self, request):
        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        user = Account.objects.get(username=username)

        Appointment.objects.create(
            user=user,
            agency=request.POST.get('agency'),
            service=request.POST.get('service'),
            appointment_date=request.POST.get('appointment_date'),
            appointment_time=request.POST.get('appointment_time'),
        )

        return redirect('myAppointments')

class MyAppointments(View):

    def get(self, request):

        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        user = Account.objects.get(
            username=username
        )

        appointments = Appointment.objects.filter(
            user=user
        ).order_by('-appointmentID')

        return render(request,
                      'my_appointments.html',
                      {
                          'appointments': appointments
                      })

    def post(self, request):

        username = request.session.get('username')

        if not username:
            return redirect('loginUser')

        user = Account.objects.get(
            username=username
        )

        appointment_id = request.POST.get('id')
        action = request.POST.get('action')

        appointment = Appointment.objects.filter(
            appointmentID=appointment_id,
            user=user
        ).first()

        if not appointment:
            return redirect('myAppointments')

        if action == "cancel":

            if appointment.status == "Pending":

                appointment.status = "Cancelled"
                appointment.save()

        elif action == "delete":

            if appointment.status == "Completed":

                appointment.delete()

        return redirect('myAppointments')

class AppointmentDashboard(View):

    def get(self, request):

        status = request.GET.get('status')

        appointments = Appointment.objects.all().order_by('-appointmentID')

        if status:
            appointments = appointments.filter(status=status)

        return render(request, 'appointment_dashboard.html', {
            'appointments': appointments
        })

    def post(self, request):

        appointment_id = request.POST.get('id')
        action = request.POST.get('action')

        try:
            appointment = Appointment.objects.get(
                appointmentID=appointment_id
            )

            if action == "confirm":
                appointment.status = "Confirmed"

            elif action == "decline":
                appointment.status = "Declined"

            elif action == "complete":
                appointment.status = "Completed"

            appointment.save()

        except Appointment.DoesNotExist:
            pass

        return redirect('appointmentDashboard')

class SubmitAppointmentSurvey(View):

    def get(self, request, appointment_id):

        appointment = Appointment.objects.get(
            appointmentID=appointment_id
        )

        return render(request,
                      'appointment_survey.html',
                      {
                          'appointment': appointment
                      })

    def post(self, request, appointment_id):

        appointment = Appointment.objects.get(
            appointmentID=appointment_id
        )

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        AppointmentSurvey.objects.create(
            appointment=appointment,
            rating=rating,
            comment=comment
        )

        return redirect('myAppointments')