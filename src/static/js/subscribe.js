


document.getElementById("contactForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const form = event.target;
    const emailAddress = form.elements.emailAddress.value;
    // console.log(emailAddress);

                if (!emailAddress) {
                  const feedback = form.querySelector('[data-sb-feedback="emailAddress:required"]');
                  feedback.classList.remove("d-none");
                  return;
                }
                const data = {
                  emailAddress: emailAddress,
                };

                fetch("/feedback", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify(data)
                })
                  .then(response => {
                    if (!response.ok) {
                      throw new Error("Network response was not ok");
                    }
                    form.reset();
                    const submitSuccessMessage = form.querySelector("#submitSuccessMessage");
                    submitSuccessMessage.classList.remove("d-none");
                  })
                  .catch(error => {
                    console.error("There was a problem with the fetch operation:", error);
                    const submitErrorMessage = form.querySelector("#submitErrorMessage");
                    submitErrorMessage.classList.remove("d-none");
                  });
  });