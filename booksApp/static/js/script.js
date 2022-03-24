document.addEventListener('DOMContentLoaded', () => {
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
  
    if ($navbarBurgers.length > 0) {
  
      $navbarBurgers.forEach( el => {
        el.addEventListener('click', () => {
  
          // Get the target from the "data-target" attribute
          const target = el.dataset.target;
          const $target = document.getElementById(target);
  
          // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
          el.classList.toggle('is-active');
          $target.classList.toggle('is-active');
  
        });
      });
    }
  
  });

const cbutton = document.querySelector('#childrenBook');

cbutton.addEventListener('click', event =>{
    fetch('/children-book-payment').then((result) => { return result.json();
    }).then((data) => {
        var stripe = Stripe(data.checkout_public_key);
        stripe.redirectToCheckout({
            sessionId: data.checkout_session_id
        }).then(function (result){
              //redirect  
        });
    })
});

const abutton = document.querySelector('#adultBook');

abutton.addEventListener('click', event =>{
    fetch('/teens-and-adult-book-payment').then((result) => { return result.json();
    }).then((data) => {
        var stripe = Stripe(data.checkout_public_key);
        stripe.redirectToCheckout({
            sessionId: data.checkout_session_id
        }).then(function (result){
              //redirect  
        });
    })
});


