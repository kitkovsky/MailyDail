const ApifyClient = require("apify-client");
const fs = require("fs");

// Initialize the ApifyClient with API token
const client = new ApifyClient({
  token: process.env.APIFY_TOKEN,
});

// Prepare actor input
const input = {
  email: process.env.MY_EMAIL,
};

(async () => {
  // Run the actor and wait for it to finish
  const run = await client.actor("vaclavrut/covid-pl").call(input);
  //Fetch and print actor results from the run's dataset (if any)
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  const extractedData = {
    dailyInfected: items[0]["dailyInfected"],
    dailyTested: items[0]["dailyTested"],
    dailyDeceased: items[0]["dailyDeceased"],
    lastUpdatedAtSource: items[0]["lastUpdatedAtSource"],
    pomeranian: {
      testedCount: items[0]["infectedByRegion"][9]["testedCount"],
      testedPositive: items[0]["infectedByRegion"][9]["testedPositive"],
    },
    lowerSilesia: {
      testedCount: items[0]["infectedByRegion"][10]["testedCount"],
      testedPositive: items[0]["infectedByRegion"][10]["testedPositive"],
    },
  };

  //let dayTable = {
  //table: []
  //};

  //dayTable.table.push(extractedData);
  //const extractedDataJSON = JSON.stringify(extractedData);
  //const JSONEDDayTable = JSON.stringify(dayTable);
  //fs.appendFile("/home/okitkowski114/DailyMail/data.json", extractedDataJSON, (err) => {
  //fs.writeFile("./data.json", JSONEDDayTable, (err) => {
  //if (err) {
  //console.error(err);
  //return;
  //}
  //});

  fs.readFile("./data.json", "utf8", function readFileCallback(err, data) {
    if (err) {
      console.error(err);
    } else {
      obj = JSON.parse(data);
      obj.table.push(extractedData);
      jsonedObj = JSON.stringify(obj);
      fs.writeFile("./data.json", jsonedObj, "utf8", (err) => {
        if (err) {
          console.error(err);
          return;
        }
      });
    }
  });
})();
