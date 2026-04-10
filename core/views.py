from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from  . import models

import time

def landing(request):
    return render(request, 'core/landing.html')

def contact(request):
    return render(request,"core/contact.html")


def home(request):
    return render(request, 'core/home.html')

def logout(request):
    request.session.flush()
    return redirect("/")


@never_cache
def userhome(request):
    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

    user_email = request.session["sunm"]

    # user ke notes
    notes = models.ShareNotes.objects.filter(owner=user_email)

    total_files = notes.count()
    shared_files = notes.filter(is_shared=True).count()

    recent_files = notes.order_by("-id")[:5]

    context = {
        "sname": request.session.get("sname"),
        "sunm": user_email,
        "total_files": total_files,
        "shared_files": shared_files,
        "recent_files": recent_files,
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

        return render(request,"core/signup.html",{"output":"User register successfully.... Please wait for admin approval or check your email to verify account"})  

def verify(request):
    vemail=request.GET.get("vemail")
    print(f"DEBUG: Verify email={vemail}")
    
    updated = models.Signup.objects.filter(email=vemail).update(status=1)
    print(f"DEBUG: Records updated={updated}")

    return render(request,"core/signup.html",{"output":"Account verified successfully.... "})  


@never_cache  
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
            
            # Clear any previous messages
            if 'output' in request.session:
                del request.session['output']

            if userDetails[0].role=="admin":
                return redirect("/myadmin/")
            else:    
                return redirect("/userhome/")
        else:
            return render(request,"core/login.html",{"output":"Invalid user or verify your account...."}) 



from django.core.files.base import ContentFile
from .utils import generate_key, encrypt_data

@never_cache
def sharenotes(request):
    
    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

    if request.method == "GET":
        return render(request,"core/sharenotes.html",
        {"sname":request.session.get("sname")})
    

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

@never_cache
def viewnotes(request):
    
    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

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

@never_cache
def generate_link(request, id):

    if "sunm" not in request.session:
      messages.error(request, "You logged out your account, please login again.")       
      return redirect("/login/")

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


@never_cache
def cpuser(request):
    #because only logged in user can change password, so we will check session for email, if not found then we will redirect to login page.
    # and the never_cache the session is expierd after the logout, so user can not access cpuser page after logout by using browser back button.
    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
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

@never_cache
def delete_note(request, id):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

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

@never_cache
def adminhome(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    return render(request,"core/adminhome.html",{"sname":request.session["sname"]})

@never_cache
def manageusers(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    userDetails=models.Signup.objects.filter(role="user")
    output = ""
    if request.GET.get("status") == "updated":
        output = "User status updated successfully...."
    return render(request,"core/manageusers.html",{"userDetails":userDetails,"sname":request.session["sname"],"output":output})    

@never_cache
def manageuserstatus(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    s=request.GET.get("s")
    regid=int(request.GET.get("regid"))

    if s=="active":
        models.Signup.objects.filter(regid=regid).update(status=1)
    elif s=="inactive":
        models.Signup.objects.filter(regid=regid).update(status=0)
    else:
        models.Signup.objects.filter(regid=regid).delete()

    return redirect("/manageusers/?status=updated")

@never_cache
def cpadmin(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
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



@never_cache
def shared_file(request, token):

    note = get_object_or_404(
        models.ShareNotes,
        share_token=token
    )

    return render(request, "core/download_page.html", {
        "token": token,
        "filename": note.original_filename
    })


@never_cache
def download_file(request, token):

    note = get_object_or_404(
        models.ShareNotes,
        share_token=token
    )

    # read encrypted file
    with note.file.open("rb") as f:
        encrypted_data = f.read()

    decrypted = decrypt_data(
        encrypted_data,
        note.encryption_key.encode()
    )

    filename = note.original_filename

    content_type, _ = mimetypes.guess_type(filename)

    temp_file = NamedTemporaryFile(delete=True)
    temp_file.write(decrypted)
    temp_file.seek(0)

    return FileResponse(
        temp_file,
        as_attachment=True,
        filename=filename,
        content_type=content_type or "application/octet-stream"
    )
