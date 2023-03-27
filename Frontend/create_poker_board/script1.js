function validate(){
    var userid=document.getElementById("user_id").value;
    var username=document.getElementById("user_name").value;
    if(userid=="shubham123" && username=="shubham"){
        alert("created successfully");
        return false;
    }
    else{
        alert("can't be created")
    }
}

