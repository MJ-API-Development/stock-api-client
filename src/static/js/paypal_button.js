  // Render the PayPal subscription button
  // noinspection JSUnresolvedVariable
                // noinspection JSUnresolvedVariable

self.addEventListener('load', async (e) => {

  paypal.Buttons({
      env: 'production', // Update the environment to production
      style: {
          shape: 'pill',
          color: 'black',
          layout: 'vertical',
          label: 'subscribe'
      },
      createSubscription: function(data, actions) {
          // Set up the subscription plan details
          const paypal_id = document.getElementById('paypal_id').value;
          return actions.subscription.create({
              env: 'production',
              plan_id: paypal_id,
          });
      },
      onInit: function(data, actions) {
          // Called when the PayPal button is first rendered
          console.log('Button initialized');
          // data: undefined
      },
      onClick: function(data, actions) {
          // Called when the PayPal button is clicked
          console.log('Button clicked');
          // data: undefined
      },
      onApprove: function(data, actions) {
          // Called when the subscription is approved by the customer
          console.log(`Subscription approved: ${JSON.stringify(data)}`);
          // Submit the form to process the subscription on the server
          // data: { subscriptionID, billingToken, facilitatorAccessToken, payerID }
          // Use the subscriptionID to retrieve subscription details from PayPal
          const form = document.getElementById('subscription-form');

          const uuid = document.getElementById('uuid').value;
          const plan_id = document.getElementById('plan_id').value;
          const paypal_id = document.getElementById('paypal_id').value;
          const subscription_id = data.subscriptionID;
          const billing_token = data.billingToken;
          const payer_id = data.payerID;
          const facilitatorAccessToken = data.facilitatorAccessToken;

          const subscription_data = {
              uuid, plan_id, paypal_id, billing_token, payer_id, subscription_id, facilitatorAccessToken
          }

          const url = '/subscribe';
          const request = new Request( url,{
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              data: JSON.stringify(subscription_data),
              mode: 'cors',
              credentials: 'same-origin'
          })

          fetch(request).then(response => {
            return response.json();
          }).then(subscription => {
              const message = subscription.message;
              const responseContainer = document.getElementById('subscription_response_message');
              responseContainer.innerHTML = `<span class="text">${message}</span>`;
              responseContainer.appendChild(create_account_button());
            })
      },
      onCancel: function(data, actions) {
          // Called when the subscription is canceled by the customer
          console.log(`Subscription canceled: ${JSON.stringify(data)}`);
          // data: { reason }
          // Display a message to the user indicating that the subscription was canceled
          window.location.href = '/'
      },
      onError: function(err) {
          // Called when an error occurs during subscription creation or approval
          console.log(`Error: ${err}`);
          // Display an error message to the user
            const responseContainer = document.getElementById('subscription_response_message');
            responseContainer.innerHTML = err;
      }
  }).render('#paypal-button-container')

});

function create_account_button() {
  const button = document.createElement('button');
  button.innerHTML = 'Proceed to your account';
  button.addEventListener('click', () => {
    window.location.href = '/account';
  });
  return button;
}
