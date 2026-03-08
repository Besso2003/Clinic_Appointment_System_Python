from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin1", password="adminpass", role="A", email="admin1@example.com"
        )
        self.doctor_user = User.objects.create_user(
            username="doctor1", password="doctorpass", role="D", email="doctor1@example.com"
        )
        self.receptionist_user = User.objects.create_user(
            username="reception1", password="receptpass", role="R", email="reception1@example.com"
        )
        self.patient_user = User.objects.create_user(
            username="patient1", password="patientpass", role="P", email="patient1@example.com"
        )

    def test_home_view_accessible(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/home.html")

    def test_patient_register_accessible_to_all(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_staff_register_access_admin_only(self):
        # Unauthenticated should be redirected to login
        response = self.client.get(reverse("staff_register"))
        self.assertEqual(response.status_code, 302)

        # Login as non-admin
        self.client.login(username="doctor1", password="doctorpass")
        response = self.client.get(reverse("staff_register"))
        self.assertEqual(response.status_code, 403)  # admin_required returns 403 for non-admins
        self.client.logout()

        # Login as admin
        self.client.login(username="admin1", password="adminpass")
        response = self.client.get(reverse("staff_register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_manage_staff_access_admin_only(self):
        # Non-admin login
        self.client.login(username="doctor1", password="doctorpass")
        response = self.client.get(reverse("manage_staff"))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Admin login
        self.client.login(username="admin1", password="adminpass")
        response = self.client.get(reverse("manage_staff"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/manage_staff.html")

    def test_view_profile_get_and_post(self):
        self.client.login(username="patient1", password="patientpass")

        # GET request
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

        # POST request with valid data
        response = self.client.post(reverse("profile"), {
            "first_name": "New",
            "last_name": "Name",
            "email": "newemail@example.com",
        })
        self.assertEqual(response.status_code, 302)  # Redirect after save
        self.client.logout()

    def test_delete_staff(self):
        # Admin cannot delete self
        self.client.login(username="admin1", password="adminpass")
        response = self.client.post(reverse("delete_staff", args=[self.admin_user.id]))
        self.assertRedirects(response, reverse("manage_staff"))
        # Should not delete self
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())

        # Admin deletes another user
        response = self.client.post(reverse("delete_staff", args=[self.doctor_user.id]))
        self.assertRedirects(response, reverse("manage_staff"))
        self.assertFalse(User.objects.filter(id=self.doctor_user.id).exists())
        self.client.logout()

    def test_view_staff_profile(self):
        self.client.login(username="admin1", password="adminpass")
        # GET request
        response = self.client.get(reverse("edit_staff", args=[self.admin_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/staff_profile.html")

        # POST request update
        response = self.client.post(reverse("edit_staff", args=[self.admin_user.id]), {
            "first_name": "Updated",
            "last_name": "Admin",
            "email": "updatedadmin@example.com",
            "username": "admin1"
        })
        self.assertRedirects(response, reverse("manage_staff"))
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.first_name, "Updated")
        self.assertEqual(self.admin_user.email, "updatedadmin@example.com")
        self.client.logout()