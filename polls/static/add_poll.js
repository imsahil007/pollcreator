

function addInput(){

     document.getElementById("submit_counter").value = "add";
     console.log('value of submit is'+document.getElementById("submit_counter"));
     document.getElementById('submit-button').click();

}
function removeInput(){
     document.getElementById("submit_counter").value = "subtract";
     document.getElementById('submit-button').click();
}
