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
        throw new Error("an error occured");
      }
      arr.push(element);
    });
    return arr;
  }

  function calcItems(amount_q, q_type) {
    if (q_type == "multiple") {
      return amount_q * 6;
    } else if (q_type == "true-false") {
      return amount_q * 4;
    } else {
      return amount_q;
    }
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
      .then((status) => {
        if (status.response == 200) {
          // setting the section's db id 
          const section_ids = status.section_ids
          // removing the dialog element
          document.querySelectorAll("dialog")[0].remove();
          var sections = document.getElementById("sections");
          sections.innerHTML += '<form id="questions-form" ></form>';
          var form = document.getElementById("questions-form");
          // creating the form
          allSections.forEach((section, index) => {
            if (section.length != 0) {
              const title = section[0][1];
              const q_type = section[1][1];
              const amount_q = section[2][1];
              form.innerHTML += `<h3 style="background-color:black; color:white;">Section: ${title}</h3>
                            <h5 style="border-bottom: 2px solid black;margin-bottom:20px">Questions:</h5>
                            <div class="section-data">
                            <input id="section_id${index}"  value="${section_ids[index]}" type="hidden">
                            </div>`;
              var section_data =
                document.querySelectorAll(".section-data")[index];
              for (var p = 1; p <= amount_q; p++) {
                section_data.innerHTML += `<p>Question${p}:<p>
                                          <input type="textarea" name="question" style="width:600px; height:60px;display:block;">`;
                if (q_type == "multiple") {
                  for (var x = 1; x < 5; x++) {
                    section_data.innerHTML += `${x}:<input type="text" name="option_value"><input type="radio" name="answer${p}-${index}"  value="${x}">`;
                  }
                } else if (q_type == "true-false") {
                  section_data.innerHTML += `<input type="text" value="True" name="option_value"><input value="1" type="radio"  name="answer${p}-${index}">
                              <input type="text" value="False" name="option_value"><input value="2" type="radio"  name="answer${p}-${index}">`;
                } else {
                  console.log("-");
                }

                section_data.innerHTML += `<br><br>`;
              }
            }
          });
          // save button
          form.innerHTML += `<button id="submit-btn" class="btn btn-primary" style="width:100%" type="button">Create Test</button>`;
          // performing the last request to save questions and options
          document
            .getElementById("submit-btn")
            .addEventListener("click", function (e) {
              const form_obj = new FormData(
                document.getElementById("questions-form")
              );
              const all_form_entries = Array.from(form_obj.entries()); // since entries return an iterator not array

              const allSectionsData = new Array();
              var temp = new Array(); // keep tracks of sections partition
              allSections.forEach((section, index) => {
                if (section.length != 0) {
                  const title = section[0][1];
                  const q_type = section[1][1];
                  const amount_q = parseInt(section[2][1]);
                  const item_amount = calcItems(amount_q, q_type); // calculates total entries of a section
                  // console.log(all_form_entries,all_form_entries.length);

                  // console.log('items calculated: ', item_amount)
                  var start = 0;
                  var questions = {};
                  var q_counter = 0; // counter for the question
                  var counter_qu_field = 0;

                  if (temp.length != 0) {
                    start = temp[temp.length - 1];
                  }

                  for (var item = start; item < start + item_amount; item++) {
                    // reading entries in section limit
                    // console.log(item, all_form_entries.length)
                    const field = all_form_entries[item];
                    // console.log("reading the field...",field);
                    if (field) {
                      // every field is an array of a pair ( field Name, value)
                      if (field[0] == "question") {
                        // initializing the question
                        console.log("question added...");
                        q_counter += 1;
                        questions["q" + q_counter] = {
                          question: field[1],
                          options: new Array(),
                          c_ans: "1",
                        };
                        counter_qu_field = 0;
                      } else if (field[0] == "option_value") {
                        console.log("option added...");
                        counter_qu_field += 1;
                        // console.log(questions["q"+q_counter],"----",questions)
                        questions["q" + q_counter]["options"].push(field[1]);
                      } else if (
                        field[0] ==
                        "answer" + q_counter + "-" + index
                      ) {
                        console.log("correct answer added");
                        questions["q" + q_counter]["c_ans"] = counter_qu_field;
                      }
                    }
                  }
                  temp.push(item);
                  // console.log('seciton finished..')
                  const this_section = {
                    section_title: title,
                    question_type: q_type,
                    amount_q: amount_q,
                    section_id: document.getElementById("section_id"+index).value,
                    questions: questions
                  };
                  allSectionsData.push(this_section);
                }
              });
              // performing the ajax to send questions and options
              const options = {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                  'data': allSectionsData

                })

              };
              fetch(url,options).then(response => response.json()).then(status =>{
                if (status['OK']=="yes"){
                  console.log('saved successfully@')
                }
              })
            });
        }
      });
  });
}
