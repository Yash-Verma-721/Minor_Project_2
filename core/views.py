from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from  . import models

import time

def landing(request):
    return render(request, 'core/landing.html')

def contact(request):
    return render(request,"core/contact.html")


def home(request):
    return render(request, 'core/home.html')
def userhome(request):
    context = {
        "sname": request.session.get("sname"),
        "sunm": request.session.get("sunm"),
        "srole": request.session.get("srole")
    }
    return render(request, "core/userhome.html", context)



from .utils import send_verification_mail
import uuid




def signup(request):
    if request.method=="GET":
        return render(request,"core/signup.html",{"output":""})
    else:
        #to recieve data from UI 'form'
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        mobile_no=request.POST.get("mobile_no")
        

        #to insert record in database using models
        p=models.Signup(name=username,email=email,password=password,mobile=mobile_no,status=0,role="user",info=time.asctime())
        p.save()

        #to integrate EmailAPI 
        

        send_verification_mail(email, username)

        return render(request,"core/signup.html",{"output":"User register successfully.... Please wait for admin approval"})  

def verify(request):
    vemail=request.GET.get("vemail")
    print(f"DEBUG: Verify email={vemail}")
    
    updated = models.Signup.objects.filter(email=vemail).update(status=1)
    print(f"DEBUG: Records updated={updated}")

    return render(request,"core/signup.html",{"output":"Account verified successfully.... "})  
    
def user_login(request):
    if request.method=="GET":    
        return render(request,"core/login.html",{"output":""})
    else:
        email=request.POST.get("email")
        password=request.POST.get("password")
        
        print(f"DEBUG: Email={email}, Password={password}")

        userDetails=models.Signup.objects.filter(email=email,password=password,status=1)
        print(f"DEBUG: Found {len(userDetails)} users")
        
        if len(userDetails)>0:
            print(f"DEBUG: User role = {userDetails[0].role}")
            request.session['sunm']=userDetails[0].email
            request.session['sname']=userDetails[0].name
            request.session['srole']=userDetails[0].role        

            if userDetails[0].role=="admin":
                return redirect("/myadmin/")
            else:    
                return redirect("/userhome/")
        else:
            return render(request,"core/login.html",{"output":"Invalid user or verify your account...."})  


# def sharenotes(request):
#     if request.method=="GET":
#         return render(request,"core/sharenotes.html",{"sname":request.session["sname"],"output":""})
#     else:

#         #to recieve data from ui
#         title=request.POST.get("title")
#         category=request.POST.get("category")
#         description=request.POST.get("description")

#         #to recive file & to push file in media folder
#         file=request.FILES["file"]
#         fs = FileSystemStorage()
#         filename = fs.save(file.name,file)

#         p=models.sharenotes(title=title,category=category,decription=description,filename=filename,uid=request.session["sunm"],info=time.asctime())
#         p.save()

#         return render(request,"core/sharenotes.html",{"sname":request.session["sname"],"output":"Content uploaded successfully....."})  
    
from django.core.files.base import ContentFile
from .utils import generate_key, encrypt_data

def sharenotes(request):

    if request.method == "GET":
        return render(request,"core/sharenotes.html",
        {"sname":request.session["sname"]})
    

    title = request.POST.get("title")
    category = request.POST.get("category")
    description = request.POST.get("description")

    uploaded_file = request.FILES["file"]

    file_data = uploaded_file.read()

    key = generate_key()
    encrypted_data = encrypt_data(file_data, key)
    
    # Save the details of uploaded file in database along with encryption key and original filename (important for download)
    note = models.ShareNotes(
        title=title,
        category=category,
        description=description,
        owner=request.session["sunm"],
        encryption_key=key.decode(),
        original_filename=uploaded_file.name,
    )
        # ✅ save encrypted file to MEDIA
    note.file.save(
        uploaded_file.name,
        ContentFile(encrypted_data)
    )
    note.save()

    return render(request,"core/sharenotes.html",
    {"sname":request.session["sname"],
     "output":" Upload File Successfully..."})


def viewnotes(request):

    notes = models.ShareNotes.objects.filter(
        owner=request.session["sunm"]
    )

    return render(
        request,
        "core/viewnotes.html",
        {
            "notes": notes,
            "sname": request.session.get("sname")
        }
    )

def generate_link(request, id):

    note = models.ShareNotes.objects.get(
        id=id,
        owner=request.session["sunm"]
    )

    note.is_shared = True
    note.save()

    link = request.build_absolute_uri(
        f"/shared/{note.share_token}"
    )

    notes = models.ShareNotes.objects.filter(
    owner=request.session["sunm"]
)

    return render(
        request,
        "core/viewnotes.html",
        {
        "notes": notes,
        "link": link,
        "sname": request.session["sname"]
        }
)



def cpuser(request):
    email=request.session["sunm"]
    name=request.session["sname"]
    if request.method=="GET":
        return render(request,"core/cpuser.html",{"sname":name,"output":""})
    else:
        opassword=request.POST.get("opassword")
        npassword=request.POST.get("npassword")
        cnpassword=request.POST.get("cnpassword")        

        userDetails=models.Signup.objects.filter(email=email,password=opassword)
        if len(userDetails)>0:
            if npassword==cnpassword:
                models.Signup.objects.filter(email=email).update(password=cnpassword)
                msg="Password changed successfully...."        
            else:
                msg="New & Confirm new password mismatch...."             
        else:
            msg="Invalid old password , please try again...."    
        return render(request,"core/cpuser.html",{"sname":name,"output":msg})
    

from django.shortcuts import get_object_or_404


def delete_note(request, id):

    note = get_object_or_404(
        models.ShareNotes,
        id=id,
        owner=request.session["sunm"]
    )

    # delete physical encrypted file
    if note.file:
        note.file.delete()

    # delete database record
    note.delete()

    return render(request, "core/viewnotes.html", {
        "notes": models.ShareNotes.objects.filter(owner=request.session["sunm"]),
        "sname": request.session.get("sname"),
        "output": "Note deleted successfully..."

    })


def adminhome(request):
    return render(request,"core/adminhome.html",{"sname":request.session["sname"]})


def manageusers(request):
    userDetails=models.Signup.objects.filter(role="user")
    output = ""
    if request.GET.get("status") == "updated":
        output = "User status updated successfully...."
    return render(request,"core/manageusers.html",{"userDetails":userDetails,"sname":request.session["sname"],"output":output})    


def manageuserstatus(request):
    s=request.GET.get("s")
    regid=int(request.GET.get("regid"))

    if s=="active":
        models.Signup.objects.filter(regid=regid).update(status=1)
    elif s=="inactive":
        models.Signup.objects.filter(regid=regid).update(status=0)
    else:
        models.Signup.objects.filter(regid=regid).delete()

    return redirect("/manageusers/?status=updated")


def cpadmin(request):
    email=request.session["sunm"]
    if request.method=="GET":
        return render(request,"core/cpadmin.html",{"sname":request.session["sname"],"output":""})
    else:
        # getting data from UI
        opassword=request.POST.get("opassword")
        npassword=request.POST.get("npassword")
        cnpassword=request.POST.get("cnpassword")  

        # userDetails me value tab hi aayegi jab user ki session email or dala hu opassword Sginup module ke parametrs se match hoga. 
        #kyuki agar user galat opassword enter krta hai hai to filter() use model se koi record nhai milega or userDetails empty rhega.
        userDetails=models.Signup.objects.filter(email=email,password=opassword)
        if len(userDetails)>0:
            if npassword==cnpassword:
                models.Signup.objects.filter(email=email).update(password=cnpassword)
                msg="Password changed successfully...."        
            else:
                msg="New & Confirm new password mismatch...."             
        else:
            msg="Invalid old password , please try again...."    
        return render(request,"core/cpadmin.html",{"sname":request.session["sname"],"output":msg})

    
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from tempfile import NamedTemporaryFile
import mimetypes
from .utils import decrypt_data


def shared_file(request, token):

    note = get_object_or_404(
        models.ShareNotes,
        share_token=token
    )

    logged_user = request.session.get("sunm")

    # OWNER OR SHARED ACCESS
    if note.owner != logged_user and not note.is_shared:
        return HttpResponse("Access Denied")

    # read encrypted file
    with note.file.open("rb") as f:
        encrypted_data = f.read()

    decrypted = decrypt_data(
        encrypted_data,
        note.encryption_key.encode()
    )

    filename = note.original_filename

    content_type, _ = mimetypes.guess_type(filename)

    # ✅ REAL FILE STREAM (IMPORTANT)
    temp_file = NamedTemporaryFile(delete=True)
    temp_file.write(decrypted)
    temp_file.seek(0)

    response = FileResponse(
        temp_file,
        as_attachment=True,
        filename=filename,
        content_type=content_type or "application/octet-stream"
    )

    return response