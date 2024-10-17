document.querySelector("dialog").showModal();

/* add section handling */
{
  const btnSection2 = document.getElementById("btn-section2");
  const btnSection3 = document.getElementById("btn-section3");
  var section2 = document.getElementById("section2");
  var section3 = document.getElementById("section3");
  btnSection3.style.display = "none";
  btnSection2.addEventListener("click", function (e) {
    section2.innerHTML = `
                <form method="GET" id="form-section2" >
                <input  id="title-input" type="text" name="title" value="SECTION2 TITLE">
                <p><span>Multiple Choice</span><span><input value="multiple" class="radio" type='radio' name="question_type" ></span>
                <p><span>True & False</span><span><input value="true-false" class="radio" type='radio' name="question_type" ></span>
                 <p><span>Declarative</span><span><input value="declarative" required class="radio" type='radio' name="question_type" ></span>
                <p>Amount Questions<input class="input-number" name="amount_questions" type="number"></p>
                </form>
                `;

    btnSection3.style.display = "block";
  });

  btnSection3.addEventListener("click", function (e) {
    section3.innerHTML = `
                <form method="GET" id="form-section3" >
                <input  id="title-input" type="text" name="title" value="SECTION2 TITLE">
                <p><span>Multiple Choice</span><span><input value="multiple" class="radio" type='radio' name="question_type" ></span>
                <p><span>True & False</span><span><input value="true-false" class="radio" type='radio' name="question_type" ></span>
                 <p><span>Declarative</span><span><input value="declarative" required class="radio" type='radio' name="question_type" ></span>
                <p>Amount Questions<input class="input-number" name="amount_questions" type="number"></p>
                </form>
                `;
  });
}

/* create-test request making and server content adding */
{
  function pushToArray(items, arr) {
    items.forEach((element) => {
      if ((element[1] == "") | (element[1] == 0)) {
        document
          .querySelectorAll("dialog")[0]
          .insertAdjacentHTML(
            "beforeend",
            '<p class="text text-danger">Please fill the form correctly</p>'
          );
        return -1;
      }
      arr.push(element);
    });
    return arr;
  }
  const btn = document.getElementById("create-test-btn");
  btn.addEventListener("click", function (e) {
    // preparing request url, headers and body
    const sec2 = document.getElementById("form-section2");
    const sec3 = document.getElementById("form-section3");
    var sec1Array = new Array();
    var sec2Array = new Array();

    var sec3Array = new Array();
    var formSec1 = new FormData(document.getElementById("form-section1"));
    var formSec2;
    var formSec3;
    // pushing section 1 form data to array
    sec1Array = pushToArray(formSec1.entries(), sec1Array);
    // pushing section 2 form data

    if (sec2) {
      formSec2 = new FormData(document.getElementById("form-section2"));
      sec2Array = pushToArray(formSec2.entries(), sec2Array);
    }
    // pushing section 3 form data
    if (sec3) {
      formSec3 = new FormData(document.getElementById("form-section3"));
      sec3Array = pushToArray(formSec3.entries(), sec3Array);
    }
    const allSections = new Array();
    allSections.push(sec1Array, sec2Array, sec3Array);
    const url =
      "http://" + document.getElementById("make-test-url").innerText.trim();

    var options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({
        meta: "1",
        duration: document.getElementById("duration").value,
        deadline: document.getElementById("deadline").value,
        start_date: document.getElementById("start").value,
        course_id: document.getElementById("course-id").value,
        sections: allSections,
      }),
    };
    // starting the http cycle
    fetch(url, options)
      .then((response) => response.json())
      .then((test_page) => {
        // removing the dialog element
        document.querySelectorAll("dialog")[0].remove();
        const sections = document.getElementById("sections");
        sections.innerHTML = `<form  id="sec-form">`;
        // inserting the formset into sections container
        test_page["sections"].forEach((sec) => {
          const sec_type = sec[0];
          const title = sec[1];
          const sec_content = sec[2];
          sections.innerHTML += `<h3 style="background-color:black; color:white;">Section: ${title}</h3>`;
          sections.innerHTML += `<h5 style="border-bottom: 2px solid black;margin-bottom:20px">Questions:</h4>
                                 <br><div data-sec-type=${sec_type} class="section-div" style="margin-left:5%;">${sec_content}</div>`;
        });
        // styling the question text input
        document.querySelectorAll("textarea").forEach((ques) => {
          ques.style = "width:600px; height:60px;display:block;";
        });
        // removing delete lables
        document.querySelectorAll("label").forEach((label) => {
          label.remove();
        });
        // removing the checkbox inputs
        document.querySelectorAll('input[type="checkbox"]').forEach((check) => {
          check.remove();
        });
        // typing the question number, inserting options
        document.querySelectorAll(".section-div").forEach((div) => {
          // editing all 3  div elements of all 3 sections
          div.querySelectorAll("p").forEach((p, index) => {
            if (index % 2 == 0) {
              // since the formset factory provides p elements which container hidden data one by one
              const section_type = div.getAttribute("data-sec-type"); // getting the section qustion type
              // adding the question number
              p.insertAdjacentHTML("afterbegin",`<strong>Question ${index / 2 + 1}</strong>:`);
              // adding options
              if (section_type == "multiple") {
                for (var x = 1; x < 5; x++) {
                  p.innerHTML += `${x}:<input type="text" name="option"><input type="checkbox" name="option" value="correct_answer">`;
                }
              } else if (section_type == "true-false") {
                p.innerHTML += `True <input type="checkbox" name="option">`;
                p.innerHTML += `False <input type="checkbox" name="option">`;
              } else {
                // declarative
                p.innerHTML += `<br>`;
              }
            }
          });
        });
        const submitBtn = document.createElement('button');
        submitBtn.type = 'button'
        submitBtn.className = "btn btn-primary"
        submitBtn.value= "Create Test"
        sections.appendChild(submitBtn)
        sections.innerHTML =  `</form>`
        
        // performing the last request to save questions and options
        
        // performing the ajax
      });
  });
}
