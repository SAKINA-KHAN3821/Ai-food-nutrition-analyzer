from flask import Blueprint, request, jsonify, render_template, session, current_app
import stripe
from backend.auth import login_required

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/create-intent', methods=['POST'])
@login_required
def create_payment_intent():
    try:
        if not current_app.config.get('STRIPE_SECRET_KEY'):
            return jsonify({'error': 'Stripe server key is not configured'}), 503

        data = request.get_json() or {}
        amount = int(data.get('amount', 0))
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400

        intent = stripe.PaymentIntent.create(
            amount=amount,  # Amount in cents (e.g., 1000 for $10)
            currency='usd',
            payment_method_types=['card'],
        )
        return jsonify({'client_secret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payment_bp.route('/success')
@login_required
def payment_success():
    session['premium'] = True  # Grant premium access
    return render_template('payment_success.html')
