import os
import instaloader
import shutil

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from .models import UserInstagramPic, UserDetail, RegisterUser, MatchedUser, RequestMeeting, ScheduleMeeting, Feedback, \
    AboutUs, ContactUs
from .serializers import (UserDetailSerializer, UserInstagramSerializer, RegisterSerializer,
                          MatchedUserSerializer, CreateMatchSerializer, DeleteMatchSerializer,
                          RequestMeetingSerializer, ScheduleMeetingSerializer, FeedbackSerializer, ContactUsSerializer,
                          AboutUsSerializer)


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateAPIView(CreateAPIView):
    model = RegisterUser
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=self.request.data)
        first_name = self.request.data['first_name']
        last_name = self.request.data['last_name']
        phone_number = self.request.data['phone_number']
        gender = self.request.data['gender']
        date_of_birth = self.request.data['date_of_birth']
        job_profile = self.request.data['job_profile']
        company_name = self.request.data['company_name']
        email = self.request.data['email']
        qualification = self.request.data['qualification']
        relationship_status = self.request.data['relationship_status']
        interests = self.request.data['interests']
        fav_quote = self.request.data['fav_quote']
        # liked_by = RegisterUser.objects.filter(id=phone_number)
        # superliked_by = RegisterUser.objects.filter(id=phone_number)
        pic_1 = self.request.data['pic_1']
        pic_2 = self.request.data['pic_2']
        pic_3 = self.request.data['pic_3']
        pic_4 = self.request.data['pic_4']
        pic_5 = self.request.data['pic_5']
        pic_6 = self.request.data['pic_6']
        pic_7 = self.request.data['pic_7']
        pic_8 = self.request.data['pic_8']
        pic_9 = self.request.data['pic_9']
        user_qs = RegisterUser.objects.filter(phone_number__iexact=phone_number)
        if user_qs.exists():
            serializer.is_valid(raise_exception=True)
            return Response({"Phone number": "User with this phone number already exists."},
                            status=HTTP_400_BAD_REQUEST)

        RegisterUser.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            gender=gender,
            date_of_birth=date_of_birth,
            job_profile=job_profile,
            company_name=company_name,
            qualification=qualification,
            relationship_status=relationship_status,
            interests=interests,
            fav_quote=fav_quote,
            # liked_by=liked_by,
            # superliked_by=superliked_by,
            pic_1=pic_1,
            pic_2=pic_2,
            pic_3=pic_3,
            pic_4=pic_4,
            pic_5=pic_5,
            pic_6=pic_6,
            pic_7=pic_7,
            pic_8=pic_8,
            pic_9=pic_9
        )
        # for x in liked_by:
        #     RegisterUser.liked_by.add(x)
        # for y in superliked_by:
        #     RegisterUser.superliked_by.add(y)
        return Response({"User": "User Created sucessfully"},
                        status=HTTP_201_CREATED)


class UserProfileAPIView(CreateAPIView):
    model = UserDetail
    serializer_class = UserDetailSerializer

    def post(self, request, *args, **kwargs):
        bio = self.request.data['bio']
        living_in = self.request.data['living_in']
        profession = self.request.data['profession']
        phone_number = self.request.data['phone_number']
        p_no = RegisterUser.objects.get(id=phone_number)
        college_name = self.request.data['college_name']
        university = self.request.data['university']
        personality = self.request.data['personality']
        interest = self.request.data['interest']
        preference_first_date = self.request.data['preference_first_date']
        fav_music = self.request.data['fav_music']
        travelled_place = self.request.data['travelled_place']
        once_in_life = self.request.data['once_in_life']
        exercise = self.request.data['exercise']
        exercise = exercise.capitalize()
        looking_for = self.request.data['looking_for']
        fav_food = self.request.data['fav_food']
        fav_pet = self.request.data['fav_pet']
        smoke = self.request.data['smoke']
        smoke = smoke.capitalize()
        drink = self.request.data['drink']
        drink = drink.capitalize()
        religion = self.request.data['religion']
        body_type = self.request.data['body_type']
        UserDetail.objects.create(
            bio=bio,
            living_in=living_in,
            profession=profession,
            phone_number=p_no,
            college_name=college_name,
            university=university,
            personality=personality,
            interest=interest,
            preference_first_date=preference_first_date,
            fav_music=fav_music,
            travelled_place=travelled_place,
            once_in_life=once_in_life,
            exercise=exercise,
            looking_for=looking_for,
            fav_food=fav_food,
            fav_pet=fav_pet,
            smoke=smoke,
            drink=drink,
            religion=religion,
            body_type=body_type
        )

        return Response({"Profile Updated": "Profile updated Successfully"}, status=HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class UserInstagramPicsAPIView(CreateAPIView):
    serializer_class = UserInstagramSerializer

    def post(self, request, *args, **kwargs):
        phone_number = self.request.data['phone_number']
        p_no = RegisterUser.objects.get(id=phone_number)
        username = self.request.data['username']
        password = self.request.data['password']
        loader = instaloader.Instaloader()
        USERNAME = username
        PASSWORD = password
        DOWNLOADED_POST_DIRECTORY = "Fetched_Posts"
        loader.login(USERNAME, PASSWORD)
        posts_array = instaloader.Profile.from_username(loader.context, USERNAME).get_posts()
        count = 0
        images = []
        number_of_posts = 0
        for post in posts_array:
            loader.download_post(post, DOWNLOADED_POST_DIRECTORY)
            number_of_posts += 1
            if number_of_posts == 10:
                break
        for f in os.listdir('./Fetched_Posts'):
            if f.endswith('.jpg'):
                while count < 10:
                    images.append(f)
                    count += 1
                    break
        UserInstagramPic.objects.create(
            phone_number=p_no,
            insta_pic_1=images[0],
            insta_pic_2=images[1],
            insta_pic_3=images[2],
            insta_pic_4=images[3],
            insta_pic_5=images[4],
            insta_pic_6=images[5],
            insta_pic_7=images[6],
            insta_pic_8=images[7],
            insta_pic_9=images[8],
            insta_pic_10=images[9],

        )
        if os.path.isdir("Fetched_Posts"):
            shutil.rmtree("Fetched_Posts")
            print("Deleted folder {} successfully".format("Fetched_Posts"))
        return Response({"Images uploaded from instagram successfully."}, status=HTTP_201_CREATED)


class UserslistAPIView(APIView):
    model = UserDetail
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        # queryset needed to be filtered
        queryset = UserDetail.objects.all().exclude(id=self.request.user.id).values()
        return Response({"Users": queryset}, status=HTTP_200_OK)

    # def post(self, request, *args, **kwargs):
    #     return self.create(request, *args, **kwargs)


class UserDetailAPIView(APIView):
    model = UserDetail
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        phone_number = self.request.data['phone_number']
        queryset = UserDetail.objects.filter(id=phone_number).values()
        return Response({"User Details": queryset}, status=HTTP_200_OK)


class SnippetFilter(rest_framework.FilterSet):
    qualification = rest_framework.CharFilter(lookup_expr='exact')
    relationship_status = rest_framework.CharFilter(lookup_expr='exact')
    religion = rest_framework.CharFilter(lookup_expr='exact')
    body_type = rest_framework.CharFilter(lookup_expr='exact')
    gender = rest_framework.CharFilter(lookup_expr='exact')
    interests = rest_framework.CharFilter(lookup_expr='exact')

    class Meta:
        model = RegisterUser
        fields = ['qualification', 'relationship_status', 'religion', 'body_type', 'gender', 'interests']
        # fileds = {
        #     'qualification': ['icontains'],
        #     'relationship_status': ['icontains'],
        #     'religion': ['icontains'],
        #     'body_type': ['icontains'],
        #     'gender': ['icontains'],
        #     'interests': ['icontains'],
        #
        # }


# class SearchUser(ListCreateAPIView):
#     model = RegisterUser
#     serializer_class = RegisterSerializer
#     filter_backends = (rest_framework.DjangoFilterBackend,)
#     filterset_class = SnippetFilter
#     queryset = RegisterUser.objects.all()

    # def get_queryset(self):
    #     queryset = RegisterUser.objects.all()
    #     print(self.request.data)
    #     qualification = self.request.GET.get('qualification', None)
    #     relationship_status = self.request.GET.get('relationship_status', None)
    #     religion = self.request.GET.get('religion', None)
    #     body_type = self.request.GET.get('body_type', None)
    #     gender = self.request.GET.get('gender', None)
    #     interests = self.request.GET.get('interests', None)
        # relationship_status = self.request.data['relationship_status']
        # religion = self.request.data['religion']
        # body_type = self.request.data['body_type']
        # gender = self.request.data['gender']
        # interests = self.request.data['interests']
        # print('Qualification ', qualification)
        # if qualification is not None:
            # queryset = RegisterUser.objects.filter(Q(qualification__exact=qualification) |
            #                                        Q(relationship_status__exact=relationship_status) |
            #                                        Q(interests__exact=interests) |
            #                                        Q(gender__exact=gender) |
            #                                        Q(religion__exact=religion) |
            #                                        Q(body_type__exact=body_type)
            #                                        )
            # print('>>>>>>>>>>>>>>>>>>>>', queryset)
        # return queryset


class SearchUser(APIView):
    model = RegisterUser
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        data = self.request.data
        qualification = self.request.data['qualification']
        relationship_status = self.request.data['relationship_status']
        religion = self.request.data['religion']
        body_type = self.request.data['body_type']
        gender = self.request.data['gender']
        interests = self.request.data['interests']
        # qualification = self.request.POST.get('qualification', None)
        # relationship_status = self.request.POST.get('relationship_status', None)
        # religion = self.request.POST.get('religion', None)
        # body_type = self.request.POST.get('body_type', None)
        # gender = self.request.POST.get('gender', None)
        # interests = self.request.POST.get('interests', None)
        if data:
            qs = RegisterUser.objects.filter(Q(qualification__exact=qualification) |
                                             Q(relationship_status__exact=relationship_status) |
                                             Q(interests__exact=interests) |
                                             Q(gender__exact=gender) |
                                             Q(religion__exact=religion) |
                                             Q(body_type__exact=body_type)
                                             )
            return Response(qs, status=HTTP_200_OK)


class GetMatchesAPIView(ListAPIView):
    model = MatchedUser
    serializer_class = MatchedUserSerializer

    def get(self, request, *args, **kwargs):
        liked_by = MatchedUser.objects.filter(liked_by=self.request.user.id)
        super_liked_by = MatchedUser.objects.filter(super_liked_by=self.request.user.id)
        liked_by_me = MatchedUser.objects.filter(liked_by_me=self.request.user.id)
        super_liked_by_me = MatchedUser.objects.filter(super_liked_by_me=self.request.user.id)
        liked_by_list = [x.id for x in liked_by]
        super_liked_by_list = [x.id for x in super_liked_by]
        liked_by_me_list = [x.id for x in liked_by_me]
        super_liked_by_me_list = [x.id for x in super_liked_by_me]
        match = []
        super_match = []
        x = set(liked_by_list) & set(liked_by_me_list)
        match.append(x)
        y = set(super_liked_by_list) & set(super_liked_by_me_list)
        super_match.append(y)
        return Response({"Matches": match, "Super Matches": super_match}, status=HTTP_200_OK)


class CreateMatchesAPIView(CreateAPIView):
    model = MatchedUser
    serializer_class = CreateMatchSerializer


class DeleteMatchesAPIView(APIView):
    model = MatchedUser
    serializer_class = DeleteMatchSerializer

    def get(self, request, *args, **kwargs):
        data = self.request.data
        liked_by_me = MatchedUser.objects.filter(liked_by_me=self.request.user.id)
        super_liked_by_me = MatchedUser.objects.filter(super_liked_by_me=self.request.user.id)
        return Response({"Likedusers": liked_by_me, "Superliked Users": super_liked_by_me}, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = self.request.data
        print('----------------', data)

        liked = self.request.data['liked_by_me']
        super_liked = self.request.data['super_liked_by_me']
        liked_by_me = MatchedUser.objects.filter(liked_by_me=self.request.user.id)
        super_liked_by_me = MatchedUser.objects.filter(super_liked_by_me=self.request.user.id)
        # print('ME------->>> ', liked_by_me, super_liked_by_me)
        # print('<<<<<<------', list(liked), list(super_liked))
        liked = list(liked)
        super_liked = list(super_liked)
        x = [str(x.id) for x in liked_by_me]
        y = [str(y.id) for y in super_liked_by_me]
        if liked in x:
            MatchedUser.objects.filter(liked_by_me=self.request.user.id).delete()
        if super_liked in y:
            MatchedUser.objects.filter(super_liked_by_me=self.request.user.id).delete()
        return Response({"User removed successfully"})


class RequestMeetingAPIView(CreateAPIView):
    model = RequestMeeting
    serializer_class = RequestMeetingSerializer

    def post(self, request, *args, **kwargs):
        phone_number = self.request.data['phone_number']
        requested_user = RegisterUser.objects.get(id=phone_number)
        liked_by_me = MatchedUser.objects.filter(liked_by_me=self.request.user.id)
        super_liked_by_me = MatchedUser.objects.filter(super_liked_by_me=self.request.user.id)
        liked_by = MatchedUser.objects.filter(liked_by=self.request.user.id)
        super_liked_by = MatchedUser.objects.filter(super_liked_by=self.request.user)
        liked_by_list = [x.id for x in liked_by]
        super_liked_by_list = [x.id for x in super_liked_by]
        liked_by_me_list = [x.id for x in liked_by_me]
        super_liked_by_me_list = [x.id for x in super_liked_by_me]
        if requested_user in liked_by_list and requested_user in liked_by_me_list:
            RequestMeeting.objects.create(
                phone_number=requested_user
            )
            return Response({"Request sent sucessfully"}, status=HTTP_200_OK)
        else:
            return Response({"Cannot send request as the user is not a match"}, status=HTTP_400_BAD_REQUEST)


class ScheduleMeetingAPIView(CreateAPIView):
    model = ScheduleMeeting
    serializer_class = ScheduleMeetingSerializer

    def post(self, request, *args, **kwargs):
        phone_number = self.request.data['phone_number']
        requested_user = RegisterUser.objects.get(id=phone_number)
        meeting_date = self.request.data['meeting_date']
        meeting_time = self.request.data['meeting_time']
        venue = self.request.data['venue']
        description = self.request.data['description']
        if self.request.user.gender == 'Female':
            ScheduleMeeting.objects.create(
                phone_number=requested_user,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                venue=venue,
                description=description
            )
            return Response({"Meeting request sent sucessfully"}, status=HTTP_200_OK)
        else:
            return Response({"Only females are allowed to sent meeting request"}, status=HTTP_400_BAD_REQUEST)


class FeedbackApiView(CreateAPIView):
    model = Feedback
    serializer_class = FeedbackSerializer


class ContactUsApiView(ListAPIView):
    model = ContactUs
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()


class AboutUsApiView(ListAPIView):
    model = AboutUs
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.all()


class FacebookSignupApiView(CreateAPIView):
    model = RegisterUser
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        return Response({"User created successfully"}, status=HTTP_201_CREATED)


class GoogleSignupView(CreateAPIView):
    model = RegisterUser
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        return Response({"User created successfully"}, status=HTTP_201_CREATED)
