import random
import re

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from email_validator import validate_email, EmailNotValidError

from .forms import (AddUserForm1, AddUserForm2, UserLoginForm, AddInternship, ManageInternship, AddIntern, add_topic,
                    ManageIntern, add_subtopic, AssignTopic, data, EditMedia, AddContributor, imageFormatting, )
from .models import (UserDetails, Internship, Intern, Topic, Subtopic, AssignedTopics, Data, Contributor,
                     ImageFormatting, HomeImages)


@login_required
def admin_add_internship(request):
    if request.user.is_superuser:
        form = AddInternship()
        if request.method == 'POST':
            internship_topic = request.POST['internship_topic']
            form = AddInternship(request.POST, request.FILES)
            if Internship.objects.filter(internship_topic=internship_topic).exists():
                messages.error(request, 'That internship already exist')
                return redirect('admin_add_internship')
            if form.is_valid():
                form.save()
                messages.success(request, 'Internship added')
                return redirect('admin_add_internship')
            else:
                messages.error(request, 'Some error occured')
                return redirect('admin_add_internship')
        form = AddInternship()
        context = {
            'form': form,
        }
        return render(request, 'fossee_math_pages/admin_add_internship.html', context)
    else:
        return redirect('dashboard')


@login_required
def admin_manage_internship(request):
    if request.user.is_superuser:
        manage_internships = Internship.objects.order_by('-internship_start_date')
        form = ManageInternship
        if request.method == 'POST':
            int_id = request.POST["id"]
            obj = get_object_or_404(Internship, id=int_id)
            form = ManageInternship(request.POST or None, instance=obj)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                messages.success(request, "Changed")
                return redirect('admin_manage_internship')
            else:
                messages.error(request, "Error")
                return redirect('admin_manage_internship')
        context = {
            'manage_internships': manage_internships,
            'form': form
        }
        return render(request, 'fossee_math_pages/admin_manage_internship.html', context)
    else:
        return redirect('dashboard')


@login_required
def admin_add_intern(request):
    if request.user.is_superuser:
        user = User.objects.all()
        interns = Intern.objects.all()
        form = AddIntern(user)
        internships = Internship.objects.all()
        if request.method == 'POST':
            intern_name = request.POST['user_id']
            topic = request.POST['internship_id']
            usr = UserDetails.objects.get(id=intern_name)
            temp1 = User.objects.get(username=usr)
            temp2 = Internship.objects.get(id=topic)
            if Intern.objects.filter(user_id=temp1).exists():
                messages.error(request, 'That intern has an internship')
                return redirect('admin_add_intern')
            data = Intern(user_id=temp1, internship_id=temp2)
            data.save()
            messages.success(request, 'Intern added with internship')
            return redirect('admin_add_intern')

        context = {
            'internships': internships,
            'form': form,
            'interns': interns,
        }
        return render(request, 'fossee_math_pages/admin_add_intern.html', context)
    else:
        return redirect('dashboard')


@login_required
def admin_view_intern(request, id):
    if request.user.is_superuser:
        datas = Intern.objects.filter(internship_id=id)
        form = ManageIntern
        if request.method == 'POST':
            int_id = request.POST["id"]
            obj = get_object_or_404(UserDetails, id=int_id)
            form = ManageIntern(request.POST or None, instance=obj)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                messages.success(request, "Changed")
                return redirect('admin_view_intern')
            else:
                messages.error(request, "Error")
                return redirect('admin_view_intern')

        context = {
            'datas': datas,
            'form': form,
        }
        return render(request, 'fossee_math_pages/admin_view_intern.html', context)
    else:
        return redirect('dashboard')


@login_required
def admin_view_intership(request):
    if request.user.is_superuser:
        internship = Internship.objects.all()
        topic = Topic.objects.all()
        subtopic = Subtopic.objects.all()

        context = {
            'internship': internship,
            'topics': topic,
            'subtopic': subtopic,
        }

        return render(request, 'fossee_math_pages/admin_view_internship.html', context)
    else:
        return redirect('dashboard')


@login_required
def admin_manage_intern(request):
    if request.user.is_superuser:
        datas = UserDetails.objects.filter(user_role="INTERN")
        form = ManageIntern
        if request.method == 'POST':
            int_id = request.POST["id"]
            obj = get_object_or_404(UserDetails, id=int_id)
            form = ManageIntern(request.POST or None, instance=obj)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                messages.success(request, "Changed")
                return redirect('admin_manage_intern')
            else:
                messages.error(request, "Error")
                return redirect('admin_manage_intern')

        context = {
            'datas': datas,
            'form': form,
        }
        return render(request, 'fossee_math_pages/admin_manage_intern.html', context)
    else:
        return redirect('dashboard')


@login_required
def admin_view_users(request):
    if request.user.is_superuser:
        datas = UserDetails.objects.all()
        user_contains_query = request.GET.get('title_contains')
        if user_contains_query != '' and user_contains_query is not None:
            datas = UserDetails.objects.filter(user_id__username__contains=user_contains_query)
        if user_contains_query == "STAFF" or user_contains_query == "staff":
            datas = UserDetails.objects.filter(user_role="STAFF")
        if user_contains_query == "INTERN" or user_contains_query == "intern":
            datas = UserDetails.objects.filter(user_role="INTERN")

        form = AddUserForm1()
        sub_form = AddUserForm2()
        if request.method == 'POST':
            # register user
            firstname = request.POST['first_name']
            lastname = request.POST['last_name']
            username = firstname + " " + lastname
            email = request.POST['email']
            user_role = request.POST['user_role']
            user_phone = request.POST['user_phone']
            user_status_inactive = 'INACTIVE'
            user_status_active = 'ACTIVE'

            regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is being used')
                return redirect('admin_view_users')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is being used')
                return redirect('admin_view_users')
            if firstname.isdigit():
                messages.error(request, 'Firstname cannot have numbers')
                return redirect('admin_view_users')
            if regex.search(firstname):
                messages.error(request, 'Firstname cannot have special characters')
                return redirect('admin_view_users')
            if lastname.isdigit():
                messages.error(request, 'Lastname cannot have numbers')
                return redirect('admin_view_users')
            if regex.search(lastname):
                messages.error(request, 'Lastname cannot have special characters')
                return redirect('admin_view_users')
            try:
                v = validate_email(email)
                val_email = v["email"]
            except EmailNotValidError as e:
                messages.error(request, 'Invalid Email ID')
                return redirect('admin_view_users')

            try:
                password = random.randint(0, 99999999)
                passwordstr = str(password)
                user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname,
                                                last_name=lastname)
                u_id = User.objects.get(username=username)

                if user_role == 'INTERN':
                    addusr = UserDetails(user_id=u_id, user_phone=user_phone, user_role=user_role,
                                         user_temp_password=password, user_status=user_status_inactive)
                    addusr.save()
                if user_role == 'STAFF':
                    user.is_staff = True
                    user.save()
                    addusr = UserDetails(user_id=u_id, user_phone=user_phone, user_role=user_role,
                                         user_temp_password=password, user_status=user_status_active)
                    addusr.save()

                send_mail(
                    'FOSSEE ANIMATION MATH',
                    'Thank you for registering with fossee_math. Your password is ' + passwordstr,
                    'fossee_math',
                    [email, 'fossee_math@gmail.com'],
                    fail_silently=True, )
            except:
                usr = User.objects.get(username=email)
                usr.delete()
                messages.error(request, 'Some error occured !')
                return redirect('admin_view_users')
            messages.success(request, 'User Added!')
            return redirect('admin_view_users')

        paginator = Paginator(datas, 25)  # Show 25 contacts per page.

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'datas': page_obj,
            'form': form,
            'sub_form': sub_form,
        }
        return render(request, 'fossee_math_pages/admin_view_users.html', context)
    else:
        return redirect('dashboard')


@login_required
def dashboard(request):
    return render(request, 'fossee_math_pages/dashboard.html')


def home_view_data(request, internship):
    print(internship)
    internship_details = Internship.objects.get(internship_topic=internship)
    id = internship_details.pk
    details = Internship.objects.get(id=id)
    topics = Topic.objects.filter(internship_id_id=id)
    subtopics = Subtopic.objects.all()

    if request.POST:
        search_contains_query = request.POST.get('title_contains')
        return home_search_results(request, search_contains_query)

    context = {
        'details': details,
        'topics': topics,
        'subtopics': subtopics,
    }
    return render(request, 'fossee_math_pages/home_view_data.html', context)


def home_details(request, subtopic):
    subtopic_request = Subtopic.objects.get(subtopic_name=subtopic)
    id = subtopic_request.pk
    subtopic_details = Subtopic.objects.get(id=id)
    contributor = ""
    ver = ""
    try:
        data = Data.objects.all()
        imagesize = ImageFormatting.objects.all()
    except Data.DoesNotExist:
        data = None
        imagesize = None

    try:
        contributor = Contributor.objects.get(topic_id=subtopic_details.topic_id)
    except:
        contributor = None

    context = {
        'subtopic': subtopic_details,
        'datas': data,
        'contributor': contributor,
        'ver': ver,
        'imagesize': imagesize,
    }
    return render(request, 'fossee_math_pages/home_details.html', context)


def index(request):
    search_contains_query = request.GET.get('title_contains')
    images = HomeImages.objects.all()

    interships = Internship.objects.filter(internship_status='COMPLETED')

    if search_contains_query != '' and search_contains_query is not None:
        return home_search_results(request, search_contains_query)

    context = {
        'internship': interships,
        'images': images,
    }

    return render(request, 'fossee_math_pages/index.html', context)


def home_search_results(request, search_contains_query):
    datas = ""
    datass = ""
    page_obj = ""
    topic = AssignedTopics.objects.all()
    data_search = Data.objects.all()

    datas = Subtopic.objects.filter(subtopic_name__icontains=search_contains_query)
    datass = Subtopic.objects.filter(topic_id__topic_name__icontains=search_contains_query)

    if datas:
        paginator = Paginator(datas, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    if datass:
        paginator = Paginator(datass, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'datas': page_obj,
        'topic': topic,
        'querry': search_contains_query,
        'data_search': data_search,
    }
    return render(request, 'fossee_math_pages/home_search_results.html', context)


@login_required
def intern_add_data(request, t_id):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        user = request.user
        e_data = Data.objects.filter(subtopic_id=t_id)
        imagesize = ImageFormatting.objects.all()
        subtopic = Subtopic.objects.get(id=t_id)
        form = data()
        context = {
            'topic': e_data,
            'form': form,
            'subtopic': subtopic,
            'imagesize': imagesize,
        }
        if request.method == 'POST':
            content = request.POST.get('data_content')
            img = request.FILES.get('image')
            video = request.FILES.get('video')

            if img is None and video is None:
                if content == "" or content == " ":
                    messages.error(request, "Fill any one of the field")
                    return render(request, "fossee_math_pages/intern_add_data.html", context)

            add_data = Data(data_content=content, data_image=img,
                            data_video=video, subtopic_id_id=t_id,
                            user_id_id=user.id)
            add_data.save()

            if img != "" or img != " ":
                imgformat = ImageFormatting(data_id_id=add_data.pk, image_width='100%', image_height='100%')
                imgformat.save()

        return render(request, 'fossee_math_pages/intern_add_data.html', context)
    else:
        return redirect('dashboard')


@login_required
def intern_update_data(request, id):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        instance = Data.objects.get(id=id)
        subtopic = Subtopic.objects.get(id=instance.subtopic_id.pk)
        t_id = instance.subtopic_id.pk
        form = data(request.POST or None, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('intern_add_data', t_id)

        context = {
            'form': form,
            'subtopic': subtopic,
        }

        return render(request, 'fossee_math_pages/intern_update_data.html', context)
    else:
        return redirect('dashboard')


@login_required
def intern_update_media(request, id):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        instance = Data.objects.get(id=id)
        subtopic = Subtopic.objects.get(id=instance.subtopic_id.pk)
        t_id = instance.subtopic_id.pk
        form = EditMedia(request.POST or None, instance=instance)
        if request.POST:
            if form.is_valid():
                img = request.FILES.get('data_image')
                video = request.FILES.get('data_video')
                instance = Data.objects.get(id=id)
                instance.data_image = img
                instance.data_video = video
                instance.data_status = "WAITING"
                instance.save()
                return redirect('intern_add_data', t_id)

        context = {
            'form': form,
            'subtopic': subtopic,
        }

        return render(request, 'fossee_math_pages/intern_update_media.html', context)
    else:
        return redirect('dashboard')


@login_required
def intern_update_image_size(request, id):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        image = Data.objects.get(id=id)
        try:
            image_size = ImageFormatting.objects.get(data_id_id=image.pk)
            form = imageFormatting(instance=image_size)
        except:
            image_size = None
            form = imageFormatting()

        if request.POST:
            image_height = request.POST.get('image_height')
            image_width = request.POST.get('image_width')
            caption = request.POST.get('image_caption')
            obj = ImageFormatting.objects.get(data_id_id=image.pk)
            obj.image_height = image_height
            obj.image_width = image_width
            obj.image_caption = caption
            obj.save()
            return redirect(intern_update_image_size, id)

        context = {
            'image': image,
            'image_size': image_size,
            'form': form,
        }

        return render(request, 'fossee_math_pages/intern_update_image_size.html', context)
    else:
        return redirect('dashboard')


@login_required
def intern_delete_data(request, id):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        instance = Data.objects.get(id=id)
        t_id = instance.subtopic_id.pk
        instance.delete()
        return redirect('intern_add_data', t_id)
    else:
        return redirect('dashboard')


@login_required
def intern_view_internship(request):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        internship = AssignedTopics.objects.get(user_id_id=request.user.id)
        topics = Topic.objects.all()
        subtopics = Subtopic.objects.all()

        context = {
            'internship': internship,
            'topics': topics,
            'subtopics': subtopics,
        }
        return render(request, 'fossee_math_pages/intern_view_internship.html', context)
    else:
        return redirect('dashboard')


@login_required
def intern_view_topic(request):
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        assigned_topic = AssignedTopics.objects.get(user_id=request.user.id)
        subtopic = Subtopic.objects.filter(topic_id=assigned_topic.topic_id)

        context = {
            'assigned': assigned_topic,
            'subtopic': subtopic,
        }
        return render(request, 'fossee_math_pages/intern_view_topic.html', context)
    else:
        return redirect('dashboard')


def internship(request):
    return render(request, 'fossee_math_pages/internship.html')


def user_login(request):
    user = None
    user = request.user

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            try:
                user = form.authenticate_user()
                login(request, user)
                if request.user.is_staff:
                    return redirect(dashboard)
                else:
                    internship = Intern.objects.get(user_id=request.user.pk)
                    internship_ststus = Internship.objects.get(id=internship.internship_id_id)
                    if internship_ststus.internship_status == 'COMPLETED':
                        form = UserLoginForm()
                        context = {
                            'form': form,
                        }
                        messages.error(request, "Internship completed")
                        logout(request)
                        return render(request, "fossee_math_pages/login.html", context)
                    else:
                        return redirect(dashboard)
                        # return render(request, "fossee_math_pages/dashboard.html")

            except:
                form = UserLoginForm()
                context = {
                    'form': form,
                }
                messages.error(request, "Invalid Email or Password")
                return render(request, "fossee_math_pages/login.html", context)
        else:
            return render(request, "fossee_math_pages/login.html", {"form": form})
    else:
        form = UserLoginForm()
        return render(request, "fossee_math_pages/login.html", {"form": form})


@login_required
def staff_add_subtopic(request, id):
    if request.user.is_staff:
        form = add_subtopic()
        i_topic = Topic.objects.get(id=id)
        subtopics = Subtopic.objects.all()

        if request.method == 'POST':
            subtopic = request.POST['subtopic']
            topic_id = request.POST['id']
            u_id = request.user.id
            data = Subtopic(subtopic_name=subtopic, topic_id_id=topic_id, user_id_id=u_id)
            data.save()
            messages.success(request, 'Topic added with internship')
            i_topic = Topic.objects.get(id=id)

        context = {
            'form': form,
            'i_topic': i_topic,
            'subtopics': subtopics,
        }
        return render(request, 'fossee_math_pages/staff_add_subtopic.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_add_topics(request):
    if request.user.is_staff:
        form = add_topic()
        internship = Internship.objects.filter(internship_status='ACTIVE').first()

        if request.method == 'POST':
            if "search_internship" in request.POST:
                internship = Internship.objects.get(pk=request.POST['search_internship'])
            else:
                topic = request.POST['topic']
                id = request.POST['id']
                u_id = request.user.id
                data = Topic(topic_name=topic, internship_id_id=id, user_id_id=u_id)
                data.save()
                messages.success(request, 'Topic added with internship')
                internship = Internship.objects.filter(internship_status='ACTIVE').first()

        internship_all = Internship.objects.all()

        topic = Topic.objects.all()

        context = {
            'form': form,
            'internship': internship,
            'internship_all': internship_all,
            'topic': topic,
        }
        return render(request, 'fossee_math_pages/staff_add_topics.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_aprove_contents(request):
    if request.user.is_staff:
        first_internship = Internship.objects.first()
        first_internship = Internship.objects.get(internship_topic=first_internship)
        internship = Internship.objects.all()
        subtopic = Subtopic.objects.all()
        assigned = AssignedTopics.objects.all()

        if "search_internship" in request.POST:
            first_internship = Internship.objects.get(pk=request.POST['search_internship'])
            subtopic = Subtopic.objects.filter(topic_id__internship_id_id=request.POST['search_internship'])

        context = {
            'assigned': assigned,
            'subtopic': subtopic,
            'internship': internship,
            'first_internship': first_internship,
        }

        return render(request, 'fossee_math_pages/staff_aprove_contents.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_manage_intern(request):
    if request.user.is_staff:
        interns = UserDetails.objects.filter(user_role="INTERN")
        internship_all = Internship.objects.all()
        form = ManageIntern() # what's happening here?
        internship = Internship.objects.first()
        interns_in = AssignedTopics.objects.filter(topic_id__internship_id_id=internship.pk)
        #print(form)
        if request.method == 'POST':
            if "search_internship" in request.POST:
                interns_in = AssignedTopics.objects.filter(topic_id__internship_id_id=request.POST['search_internship'])
                internship = Internship.objects.get(pk=request.POST['search_internship'])    # should be at
                #print(interns_in)
            else:
                int_id = request.POST["id"]
                obj = get_object_or_404(UserDetails, id=int_id)
                form = ManageIntern(request.POST or None, instance=obj)
                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.save()
                    messages.success(request, "Changed")
                    return redirect('staff_manage_intern')
                else:
                    messages.error(request, "Error")
                    return redirect('staff_manage_intern')

        context = {
            'interns': interns,
            'form': form,
            'internship_all': internship_all,
            'interns_in': interns_in,
            'chosen_internship': internship
        }
        #print(context)
        return render(request, 'fossee_math_pages/staff_manage_intern.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_assign_topic(request):
    if request.user.is_staff:
        user = User.objects.all()
        form = AssignTopic(user)
        inters = User.objects.filter(is_staff=False, is_superuser=False)
        internship = Internship.objects.all()
        first_internsip = Internship.objects.filter(internship_status='ACTIVE').first()
        i_topic = Topic.objects.all()
        as_topic = AssignedTopics.objects.filter(topic_id__internship_id=first_internsip)

        if request.method == 'POST':
            if "search_internship" in request.POST:

                first_internsip = Internship.objects.get(pk=request.POST['search_internship'])
                print(first_internsip)
                try:
                    as_topic = AssignedTopics.objects.filter(topic_id__internship_id_id=first_internsip.pk)
                except:
                    as_topic = None
            else:
                if request.method == "POST":
                    intern_name = request.POST['user_id']
                    topic = request.POST['topic_id']
                    usr = UserDetails.objects.get(id=intern_name)
                    temp1 = User.objects.get(id=usr.user_id_id)
                    temp2 = Topic.objects.get(id=topic)
                    if AssignedTopics.objects.filter(user_id=temp1).exists():
                        messages.error(request, 'That intern has an assigned topic')
                        return redirect('staff_assign_topic')
                    elif AssignedTopics.objects.filter(topic_id=temp2).exists():
                        messages.error(request, 'That topic is assigned alredy')
                        return redirect('staff_assign_topic')
                    else:
                        data = AssignedTopics(user_id=temp1, topic_id=temp2)
                        data.save()
                        messages.success(request, 'Intern assigned with topic')

        context = {
            'interns': inters,
            'form': form,
            'intern': internship,
            'as_topic': as_topic,
            'i_topic': i_topic,
            'chosen_inernship': first_internsip,
        }
        return render(request, 'fossee_math_pages/staff_assign_topic.html', context)
    else:
        return redirect('dashboard')


# @login_required
# def staff_view_interns(request):
#     if request.user.is_staff:
#         topics = AssignedTopics.objects.all()
#         internship_all = Internship.objects.all()
#         internship = Internship.objects.first()
#         internship = Internship.objects.get(pk=internship.pk)
#
#         if "search_internship" in request.POST:
#             internship = Internship.objects.get(pk=request.POST['search_internship'])
#
#         conxext = {
#             'topics': topics,
#             'internship': internship,
#             'internship_all': internship_all,
#         }
#         return render(request, 'fossee_math_pages/staff_view_interns.html', conxext)
#     else:
#         return redirect('dashboard')


@login_required
def staff_view_internship(request):
    if request.user.is_staff:
        internship = Internship.objects.first()
        internship = Internship.objects.filter(pk=internship.pk)
        topics = Topic.objects.all()
        subtopics = Subtopic.objects.all()
        assigned = AssignedTopics.objects.all()
        internship_all = Internship.objects.all()

        if "search_internship" in request.POST:
            internship = Internship.objects.filter(pk=request.POST['search_internship'])

        context = {
            'internship': internship,
            'topics': topics,
            'subtopics': subtopics,
            'assigned': assigned,
            'internship_all': internship_all,
            'chosen_internship': internship[0],
        }
        return render(request, 'fossee_math_pages/staff_view_internship.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_view_topic(request, s_id):
    if request.user.is_staff:
        subtopic = Subtopic.objects.get(id=s_id)
        data = Data.objects.filter(subtopic_id=subtopic.pk)
        imageformat = ImageFormatting.objects.all()

        context = {
            'subtopic': subtopic,
            'datas': data,
            'imagesize': imageformat,
        }

        return render(request, 'fossee_math_pages/staff_view_topic.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_update_data(request, id):
    if request.user.is_staff:
        instance = Data.objects.get(id=id)
        subtopic = Subtopic.objects.get(id=instance.subtopic_id.pk)
        t_id = instance.subtopic_id.pk
        form = data(request.POST or None, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('staff_view_topic', t_id)

        context = {
            'form': form,
            'subtopic': subtopic,
        }

        return render(request, 'fossee_math_pages/staff_update_data.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_update_image_size(request, id):
    if request.user.is_staff:
        image = Data.objects.get(id=id)
        try:
            image_size = ImageFormatting.objects.get(data_id_id=image.pk)
            form = imageFormatting(instance=image_size)
        except:
            image_size = None
            form = imageFormatting()

        if request.POST:
            image_height = request.POST.get('image_height')
            image_width = request.POST.get('image_width')
            caption = request.POST.get('image_caption')
            obj = ImageFormatting.objects.get(data_id_id=image.pk)
            obj.image_height = image_height
            obj.image_width = image_width
            obj.image_caption = caption
            obj.save()
            return redirect(staff_update_image_size, id)

        context = {
            'image': image,
            'image_size': image_size,
            'form': form,
        }

        return render(request, 'fossee_math_pages/staff_update_image_size.html', context)
    else:
        return redirect('dashboard')


@login_required
def staff_aprove_subtopic(request, id):
    if request.user.is_staff:
        instance = Subtopic.objects.get(id=id)
        t_id = instance.pk
        instance.subtopic_status = "ACCEPTED"
        instance.save()
        return redirect('staff_aprove_contents')
    else:
        return redirect('dashboard')


@login_required
def staff_reject_subtopic(request, id):
    if request.user.is_staff:
        instance = Subtopic.objects.get(id=id)
        t_id = instance.pk
        instance.subtopic_status = "REJECTED"
        instance.save()
        return redirect('staff_aprove_contents')
    else:
        return redirect('dashboard')


@login_required
def staff_delete_data(request, id):
    if request.user.is_staff:
        instance = Data.objects.get(id=id)
        t_id = instance.subtopic_id.pk
        instance.delete()
        return redirect('staff_view_topic', t_id)
    else:
        return redirect('dashboard')


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def staff_add_contribution(request, id):
    if request.user.is_staff:
        try:
            instance = Contributor.objects.get(topic_id=id)
            form = AddContributor(request.POST or None, instance=instance)
        except:
            instance = None
            form = AddContributor()

        assigned = AssignedTopics.objects.get(topic_id=id)

        if request.POST:
            if instance is not None:
                obj = form.save(commit=False)
                obj.save()
            else:
                internname = request.POST['username']
                mentorname = request.POST['mentor']
                professorname = request.POST['professor']
                obj = Contributor(topic_id=Topic.objects.get(id=id), contributor=internname, mentor=mentorname,
                                  professor=professorname)
                obj.save()
        try:
            instance = Contributor.objects.get(topic_id=id)
            form = AddContributor(request.POST or None, instance=instance)
        except:
            instance = None
            form = AddContributor()

        context = {
            'form': form,
            'assigned': assigned,
        }
        return render(request, 'fossee_math_pages/staff_add_contributor.html', context)
    else:
        return redirect('dashboard')


def error_404_view(request, exception):
    return render(request, 'fossee_math_pages/404.html')
