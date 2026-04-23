from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from .authz import get_user_role
from .models import Classroom, Course, Enrollment, Grade, Student, UserProfile


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "ma_sv",
            "ho_ten",
            "ngay_sinh",
            "gioi_tinh",
            "email",
            "so_dien_thoai",
            "khoa",
            "nganh",
            "lop",
            "khoa_hoc",
            "trang_thai",
        ]
        widgets = {
            "ngay_sinh": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "ma_sv": "Ma sinh vien",
            "ho_ten": "Ho ten",
            "ngay_sinh": "Ngay sinh",
            "gioi_tinh": "Gioi tinh",
            "email": "Email",
            "so_dien_thoai": "So dien thoai",
            "khoa": "Khoa",
            "nganh": "Nganh",
            "lop": "Lop",
            "khoa_hoc": "Khoa hoc",
            "trang_thai": "Trang thai",
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["ma_hp", "ten_hp", "so_tin_chi"]
        labels = {
            "ma_hp": "Ma hoc phan",
            "ten_hp": "Ten hoc phan",
            "so_tin_chi": "So tin chi",
        }


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = [
            "ma_lop_hp",
            "course",
            "giang_vien",
            "hoc_ky",
            "nam_hoc",
            "phong_hoc",
            "lich_hoc",
            "si_so_toi_da",
            "trang_thai",
        ]
        labels = {
            "ma_lop_hp": "Ma lop hoc phan",
            "course": "Hoc phan",
            "giang_vien": "Giang vien",
            "hoc_ky": "Hoc ky",
            "nam_hoc": "Nam hoc",
            "phong_hoc": "Phong hoc",
            "lich_hoc": "Lich hoc",
            "si_so_toi_da": "Si so toi da",
            "trang_thai": "Trang thai",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_model = get_user_model()
        teacher_qs = user_model.objects.filter(
            Q(is_superuser=True)
            | Q(profile__role=UserProfile.Role.GIANG_VIEN, profile__status=UserProfile.Status.ACTIVE)
        ).distinct()
        self.fields["giang_vien"].queryset = teacher_qs.order_by("username")
        self.fields["giang_vien"].required = True


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "classroom", "trang_thai"]
        labels = {
            "student": "Sinh vien",
            "classroom": "Lop hoc phan",
            "trang_thai": "Trang thai",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.exclude(trang_thai=Student.Status.SOFT_DELETED).order_by("ma_sv")
        self.fields["classroom"].queryset = Classroom.objects.select_related("course", "giang_vien").order_by(
            "-nam_hoc", "-hoc_ky", "ma_lop_hp"
        )

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        classroom = cleaned_data.get("classroom")

        if not student or not classroom:
            return cleaned_data

        enrollments_for_class = Enrollment.objects.filter(classroom=classroom)
        if self.instance.pk:
            enrollments_for_class = enrollments_for_class.exclude(pk=self.instance.pk)

        if enrollments_for_class.count() >= classroom.si_so_toi_da:
            self.add_error("classroom", "Lop hoc phan da du si so toi da.")

        duplicate = Enrollment.objects.filter(
            student=student,
            course=classroom.course,
            hoc_ky=classroom.hoc_ky,
            nam_hoc=classroom.nam_hoc,
        )
        if self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)

        if duplicate.exists():
            self.add_error("classroom", "Sinh vien da dang ky hoc phan nay trong hoc ky va nam hoc da chon.")

        return cleaned_data


class StudentEnrollmentForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.none(), label="Lop hoc phan")

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)

        if not self.student:
            self.fields["classroom"].queryset = Classroom.objects.none()
            return

        open_classes = Classroom.objects.select_related("course", "giang_vien").filter(
            trang_thai=Classroom.Status.OPEN
        )
        enrolled_class_ids = Enrollment.objects.filter(student=self.student).exclude(classroom__isnull=True).values_list(
            "classroom_id", flat=True
        )
        self.fields["classroom"].queryset = open_classes.exclude(id__in=enrolled_class_ids).order_by(
            "-nam_hoc", "-hoc_ky", "ma_lop_hp"
        )

    def clean_classroom(self):
        classroom = self.cleaned_data["classroom"]

        if Enrollment.objects.filter(classroom=classroom).count() >= classroom.si_so_toi_da:
            raise forms.ValidationError("Lop hoc phan da du si so toi da.")

        already_registered_course = Enrollment.objects.filter(
            student=self.student,
            course=classroom.course,
            hoc_ky=classroom.hoc_ky,
            nam_hoc=classroom.nam_hoc,
        ).exists()
        if already_registered_course:
            raise forms.ValidationError("Ban da dang ky hoc phan nay trong hoc ky va nam hoc nay.")

        return classroom

    def save(self) -> Enrollment:
        classroom = self.cleaned_data["classroom"]
        enrollment = Enrollment.objects.create(
            student=self.student,
            classroom=classroom,
            course=classroom.course,
            hoc_ky=classroom.hoc_ky,
            nam_hoc=classroom.nam_hoc,
            trang_thai=Enrollment.Status.DANG_HOC,
        )
        return enrollment


class GradeInputForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.none(), label="Sinh vien")

    class Meta:
        model = Grade
        fields = ["enrollment", "diem_chuyen_can", "diem_qua_trinh", "diem_thi", "lan_hoc"]
        labels = {
            "enrollment": "Dang ky hoc phan",
            "diem_chuyen_can": "Diem chuyen can",
            "diem_qua_trinh": "Diem qua trinh",
            "diem_thi": "Diem thi",
            "lan_hoc": "Lan hoc",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        role = get_user_role(user)
        student_qs = Student.objects.exclude(trang_thai=Student.Status.SOFT_DELETED).order_by("ma_sv")
        enrollment_qs = Enrollment.objects.select_related("student", "course", "classroom").order_by(
            "-nam_hoc", "-hoc_ky", "course__ma_hp"
        )

        if role == UserProfile.Role.GIANG_VIEN and user and not user.is_superuser:
            enrollment_qs = enrollment_qs.filter(classroom__giang_vien=user)
            student_qs = student_qs.filter(enrollments__in=enrollment_qs).distinct()

        self.fields["student"].queryset = student_qs
        self.fields["student"].empty_label = "Chon sinh vien"

        selected_student_id = None
        selected_enrollment_id = None

        if self.is_bound:
            selected_student_id = self.data.get("student")
            selected_enrollment_id = self.data.get("enrollment")
        else:
            if self.initial.get("student"):
                selected_student_id = str(self.initial["student"])
            if self.initial.get("enrollment"):
                selected_enrollment_id = str(self.initial["enrollment"])

        if selected_student_id:
            enrollment_qs = enrollment_qs.filter(student_id=selected_student_id)
        elif selected_enrollment_id:
            enrollment_qs = enrollment_qs.filter(id=selected_enrollment_id)
        else:
            enrollment_qs = Enrollment.objects.none()

        self.fields["enrollment"].queryset = enrollment_qs
        self.fields["enrollment"].empty_label = "Chon dang ky hoc phan"
        self.field_order = ["student", "enrollment", "diem_chuyen_can", "diem_qua_trinh", "diem_thi", "lan_hoc"]

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        enrollment = cleaned_data.get("enrollment")

        if student and enrollment and enrollment.student_id != student.id:
            self.add_error("enrollment", "Dang ky hoc phan khong thuoc sinh vien da chon.")

        return cleaned_data
