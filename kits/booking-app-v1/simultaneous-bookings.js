// Simultaneous booking test (check T05), for the class-booking checklist of AI Builder Marketplace.
// Run it in the browser console ON YOUR OWN TEST APP, on an empty 8-spot class. It sends ten booking
// requests at the same moment to the app's own booking endpoint and prints what came back.
// 1. Book one class normally with the browser's network tab open, and copy the request URL and body.
// 2. Fill in ENDPOINT and makeBody below to match what your app sent.
// 3. Paste this file into the console and run it. Then count the bookings on the admin page:
//    8 accepted and 2 refused is a pass; 9 or 10 accepted is a fail.
const ENDPOINT = "/api/bookings";            // <- change to your app's booking URL
const makeBody = (n) => ({                   // <- change the field names to match your app
  classId: "PUT-THE-CLASS-ID-HERE",
  name: "Test " + (100 + n),
  email: "yoga.test+" + (100 + n) + "@example.com",
});
Promise.all(Array.from({ length: 10 }, (_, n) =>
  fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(makeBody(n)) })
    .then(r => r.status + " " + r.statusText).catch(e => "error " + e)))
  .then(res => console.table(res));
