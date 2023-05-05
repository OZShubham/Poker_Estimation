function myfunc(){

     var selectcheckbox = document.getElementById("select_all");
    
    
    
    if(selectcheckbox.checked == true){
    
    var allcheckbox = document.getElementsByName("user_id");
    
    for(var i=0 ;i<allcheckbox.length; i++){
    
    allcheckbox[i].checked = true;
    
    }
    
    }
    
    else{
    
    var allcheckbox = document.getElementsByName("user_id");
    
    for(var i=0 ;i<allcheckbox.length; i++){
    allcheckbox[i].checked = false;
    
    }
}
    
}