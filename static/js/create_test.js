document.querySelector('dialog').showModal()

/* add section handling */
{
const btnSection2 = document.getElementById("btn-section2");
const btnSection3 = document.getElementById("btn-section3");
var section2 = document.getElementById("section2");
var section3 = document.getElementById("section3");
btnSection3.style.display = "none"
btnSection2.addEventListener('click', function(e){

    section2.innerHTML = `<input  id="title-input" type="text" value="SECTION2 TITLE">
                <p><span>Four Options</span><span><input class="radio" type='radio' name="type_option" ></span>
                <p><span>True & False</span><span><input class="radio" type='radio' name="type_option" ></span>
                <p>Amount Questions<input class="input-number" name="amount_questions" type="number"></p>`;   
    
    btnSection3.style.display = "block"
})  

btnSection3.addEventListener("click", function(e){
    section3.innerHTML = `<input  id="title-input" type="text" value="SECTION2 TITLE">
                <p><span>Four Options</span><span><input class="radio" type='radio' name="type_option" ></span>
                <p><span>True & False</span><span><input class="radio" type='radio' name="type_option" ></span>
                <p>Amount Questions<input class="input-number" name="amount_questions" type="number"></p>`;
})
}

/* create-test request making */
{
const btn = document.getElementById('create-test-btn');
btn.addEventListener('click', function(e){
    // preparing request url, headers and body
    const url = "http://" + document.getElementById("make-test-url").innerText.trim();
    var options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({
        "meta":"1",
        "duration": document.getElementById("duration").value,
        "deadline" : document.getElementById("deadline").value,
        "start_date" : document.getElementById("start").value,
        "course_id": document.getElementById("course-id").value,
        "form": document.querySelectorAll('form')[0],
        "sections":{
                
        }
      })
    };
    // starting the http cycle
    console.log(url)
    fetch(url, options).then(response => response.json()).then(test_page => {
        console.log('overriding the test page...')
        document.body.innerHTML = test_page['page']
        console.log("ok!")
    })

})
}