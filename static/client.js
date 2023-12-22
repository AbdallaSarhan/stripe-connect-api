var stripe = Stripe("your_stripe_public_key");
var elements = stripe.elements();
var cardElement = elements.create("card");

cardElement.mount("#card-element");

var paymentForm = document.getElementById("payment-form");
var paymentStatus = document.getElementById("payment-status");

paymentForm.addEventListener("submit", function (event) {
    event.preventDefault();
    payWithCard();
});

function payWithCard() {
    stripe
        .confirmCardPayment("your_payment_intent_client_secret", {
            payment_method: {
                card: cardElement,
            },
        })
        .then(function (result) {
            if (result.error) {
                // Show error to your customer
                showError(result.error.message);
            } else {
                // The payment succeeded!
                orderComplete(result.paymentIntent.id);
            }
        });
}

function orderComplete(paymentIntentId) {
    paymentStatus.textContent = "Payment succeeded!";
    // You can add additional logic here, such as updating a database or displaying a success message to the user.
}