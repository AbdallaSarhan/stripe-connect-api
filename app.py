from flask import Flask, render_template, request, jsonify
import stripe


# Set your Stripe API keys
stripe.api_key = "your_stripe_secret_key"

# Define your endpoint secret for webhook events
endpoint_secret = "your_stripe_endpoint_secret"

# Replace the following with your platform account ID
PLATFORM_ACCOUNT_ID = "acct_1234567890"

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    return render_template("index.html")


# Route for creating a PaymentIntent
@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    data = request.json
    payment_intent = stripe.PaymentIntent.create(
        amount=data["amount"],
        currency="usd",
        payment_method=data["payment_method"],
        confirmation_method="manual",
        confirm=True,
        application_fee_amount=int(data["amount"] * 0.1),
        transfer_data={"destination": PLATFORM_ACCOUNT_ID},
    )

    return generate_response(payment_intent)

# Webhook endpoint to handle events
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print("Invalid payload")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Invalid signature")
        return "Invalid signature", 400

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]  # contains a stripe.PaymentIntent
        print("PaymentIntent was successful!")

    return "", 200

# Helper function to generate a JSON response
def generate_response(payment_intent):
    status = payment_intent["status"]
    if status == "requires_action" or status == "requires_source_action":
        return jsonify(
            requires_action=True,
            payment_intent_client_secret=payment_intent.client_secret,
        )
    elif status == "succeeded":
        return jsonify(success=True)



if __name__ == '__main__':
    app.run(debug=True, port=5000)
