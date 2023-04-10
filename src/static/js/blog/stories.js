//
//
// document.getElementById('load_articles').addEventListener('click', async (event) => {
//   event.preventDefault(); // prevent the default form submission behavior
//   const load_stories_button = document.getElementById('load_articles');
//   load_stories_button.disabled = true;
//   try {
//     const form = document.getElementById('story');
//     const formData = new FormData(form);
//     const response = await fetch(form.action, {
//       method: form.method,
//       body: formData,
//     });
//     document.body.innerHTML = await response.text(); // parse the response as text
//   } catch (error) {
//     // Handle any errors that occur during the form submission...
//       load_stories_button.disabled = false;
//   } finally {
//     load_stories_button.disabled = false;
//   }
// });
