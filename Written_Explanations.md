## Part B: Debug Explanations
* **Bug 1: The Server Crashes if the Farmer is Missing.** 
If the mobile app tries to update a farmer ID that does not exist in the database, the code completely breaks and crashes the server (a "KeyError"). Instead of crashing, the code should safely intercept the mistake and politely reply with a "404 Not Found" error.

* **Bug 2: Accepting Fake Statuses.** 
The current code blindly accepts whatever text the mobile app sends. A glitchy phone could accidentally change a farmer's status to "BANANA", and the database would save it. The code needs strict validation to ensure it only accepts the exact legal statuses: "PENDING", "VERIFIED", or "FLAGGED".

* **Bug 3: Forcing the Phone to Guess the Result.** 
When an update is successful, the server just replies with a generic "Status updated" message. Because the mobile app has a slow internet connection, it now has to make a second request just to see what the newly updated database record looks like. The server should reply with the completely updated farmer profile immediately so the phone can sync perfectly in one step.

## Part C
**Answer 1: Handling Duplicate Submissions Safely**

To safely handle duplicate submissions, the mobile app should generate a unique "receipt number" (an Idempotency Key) the moment the agent clicks Save. It sends this number along with the farm data.

When the backend receives the data, it quickly checks if it has seen this receipt number before.

* If it is a new number, we save the farm data and store the receipt number.

* If a bad internet connection causes the phone to accidentally send the exact same data again, the backend recognizes the old receipt number.

Instead of saving the farm twice or throwing an error, the backend just says, "I already processed this," and sends back a success message. 
This allows the mobile app to safely retry as many times as it needs to without corrupting the database.


**Answer 2: The Danger of Phone Timestamps**

Trusting the time sent by a mobile phone is dangerous for legal compliance.
Phone clocks can naturally fall out of sync when offline, or a dishonest agent could manually change their phone's clock to fake when they visited a farm to beat a deadline.

To fix this, we cannot rely solely on the phone's word. The backend must record its own independent, globally synced "server time" the exact second it receives the data. This server timestamp becomes the official truth for European audits.

We still save the phone's submitted time, but only to compare the two later. If there is a massive unexplained difference between the phone's claim and the server's truth, our system can automatically flag the record for review.