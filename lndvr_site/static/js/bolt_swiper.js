document.addEventListener("DOMContentLoaded", function () {
  const swiper = new Swiper(".bolt-swiper", {
    loop: false,           // you can set true if you want continuous loop
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 30,
    autoplay: {
      delay: 4000,          // 4 seconds per slide
      disableOnInteraction: false, // continue autoplay after user interacts
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
  });
});
