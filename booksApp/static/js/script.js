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


