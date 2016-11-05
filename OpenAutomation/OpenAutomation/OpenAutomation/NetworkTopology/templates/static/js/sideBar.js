function openNav(bool){
    if (typeof bool == "undefined") bool=true;
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    document.getElementById("dimmer").style.display=(bool?'block':'none');
    document.getElementById("openButton").style.display="none";
}

function closeNav(bool){
    if (typeof bool == "undefined") bool=true;
    document.getElementById("mySidenav").style.width = "30px";
    document.getElementById("main").style.marginLeft= "0";
    document.getElementById("dimmer").style.display=(bool?'block':'none');
    document.getElementById("openButton").style.display="inline";
}