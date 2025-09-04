document.addEventListener("DOMContentLoaded", function() {
  const swiper = new Swiper('.bolt-swiper', {
    loop: true,
    spaceBetween: 40,
    effect: 'fade',
    fadeEffect: { crossFade: true },
    speed: 800,
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
      dynamicBullets: true,
    },
    autoplay: {
      delay: 3000,
      disableOnInteraction: false,
    },
    keyboard: { enabled: true },
  });
});