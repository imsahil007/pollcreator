

function clipboard(element){
    var link = document.getElementById("clipboard-link");

    /* Select the text field */
    link.select();
    link.setSelectionRange(0, 99999); /*For mobile devices*/
  
    /* Copy the text inside the text field */
    document.execCommand("copy");
  
    /* Alert the copied text */
    alert("Copied the link: " + link.value);

}

