from django import forms

from .models import Course, Enrollment, Grade, Student


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
            "ma_sv": "Mã sinh viên",
            "ho_ten": "Họ tên",
            "ngay_sinh": "Ngày sinh",
            "gioi_tinh": "Giới tính",
            "email": "Email",
            "so_dien_thoai": "Số điện thoại",
            "khoa": "Khoa",
            "nganh": "Ngành",
            "lop": "Lớp",
            "khoa_hoc": "Khóa học",
            "trang_thai": "Trạng thái",
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["ma_hp", "ten_hp", "so_tin_chi"]
        labels = {
            "ma_hp": "Mã học phần",
            "ten_hp": "Tên học phần",
            "so_tin_chi": "Số tín chỉ",
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course", "hoc_ky", "nam_hoc", "trang_thai"]
        labels = {
            "student": "Sinh viên",
            "course": "Học phần",
            "hoc_ky": "Học kỳ",
            "nam_hoc": "Năm học",
            "trang_thai": "Trạng thái",
        }


class GradeInputForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.exclude(trang_thai=Student.Status.SOFT_DELETED).order_by("ma_sv"),
        label="Sinh viên",
    )

    class Meta:
        model = Grade
        fields = ["enrollment", "diem_chuyen_can", "diem_qua_trinh", "diem_thi", "lan_hoc"]
        labels = {
            "enrollment": "Đăng ký học phần",
            "diem_chuyen_can": "Điểm chuyên cần",
            "diem_qua_trinh": "Điểm quá trình",
            "diem_thi": "Điểm thi",
            "lan_hoc": "Lần học",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_order = ["student", "enrollment", "diem_chuyen_can", "diem_qua_trinh", "diem_thi", "lan_hoc"]
        self.fields["student"].empty_label = "Chọn sinh viên"

        student_qs = Student.objects.exclude(trang_thai=Student.Status.SOFT_DELETED).order_by("ma_sv")
        self.fields["student"].queryset = student_qs

        selected_student_id = None
        if self.is_bound:
            selected_student_id = self.data.get("student")
        elif self.initial.get("student"):
            selected_student_id = str(self.initial.get("student"))

        enrollment_qs = Enrollment.objects.select_related("student", "course").order_by(
            "-nam_hoc",
            "-hoc_ky",
            "course__ma_hp",
        )
        if selected_student_id:
            enrollment_qs = enrollment_qs.filter(student_id=selected_student_id)
        else:
            enrollment_qs = Enrollment.objects.none()

        self.fields["enrollment"].queryset = enrollment_qs
        self.fields["enrollment"].empty_label = "Chọn đăng ký học phần"

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        enrollment = cleaned_data.get("enrollment")
        if student and enrollment and enrollment.student_id != student.id:
            self.add_error("enrollment", "Đăng ký học phần không thuộc sinh viên đã chọn.")
        return cleaned_data
