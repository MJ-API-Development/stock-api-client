/**
 * Incase of phones reduce image sizes
 */
document.addEventListener('load', async (event) => {
    const image = document.querySelector('.image');
    if (window.innerWidth < 768) {
      image.style.width = '50%';
    } else {
      image.style.width = '100%';
    }
});
