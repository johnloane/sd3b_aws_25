let aliveSecond = 0;
let heartBeatRate = 5000;
let pubnub;
// Channel must match that in the pubub_sensors.py code on the pi
let appChannel = "johns_pi_channel";

function time() {
  let d = new Date();
  let currentSecond = d.getTime();
  if (currentSecond - aliveSecond > heartBeatRate + 1000) {
    document.getElementById("connection_id").innerHTML = "DEAD";
  } else {
    document.getElementById("connection_id").innerHTML = "ALIVE";
  }
  setTimeout("time()", 1000);
}

function keepAlive() {
  fetch("/keep_alive")
    .then((response) => {
      if (response.ok) {
        let date = new Date();
        aliveSecond = date.getTime();
        return response.json();
      }
      throw new Error("Server offline");
    })
    .catch((error) => console.log(error));
  setTimeout("keepAlive()", heartBeatRate);
}

function handleClick(cb) {
  if (cb.checked) {
    value = "on";
  } else {
    value = "off";
  }
  console.log("Publishing to PubNub");
  publishMessage({ buzzer: value });
}

const setupPubNub = () => {
  pubnub = new PubNub({
    publishKey: "pub-c-1bbfa82c-946c-4344-8007-85d2c1061101",
    subscribeKey: "sub-c-88506320-2127-11eb-90e0-26982d4915be",
    userId: "John",
  });

  const channel = pubnub.channel(appChannel);
  //create a subscription
  const subscription = channel.subscription();

  pubnub.addListener({
    status: (s) => {
      console.log("Status", s.category);
    },
  });

  subscription.onMessage = (messageEvent) => {
    handleMessage(messageEvent.message);
  };
  subscription.subscribe();
  sendEvent("get_user_token");
};

const publishMessage = async (message) => {
  const publishPayload = {
    channel: appChannel,
    message: message,
  };
  await pubnub.publish(publishPayload);
};

function handleMessage(message) {
  if (message == '"Motion":"Yes"') {
    document.getElementById("motion_id").innerHTML = "Motion";
  }
  if (message == '"Motion":"No"') {
    document.getElementById("motion_id").innerHTML = "No Motion";
  }
}

function logout() {
  location.replace("/logout");
}

function grantAccess(ab) {
  let userId = ab.id.split("-")[2];
  let readState = document.getElementById("read-user-" + userId).checked;
  let writeState = document.getElementById("write-user-" + userId).checked;
  console.log("grant-" + userId + "-" + readState + "-" + writeState);
  sendEvent("grant-" + userId + "-" + readState + "-" + writeState);
}

function sendEvent(value) {
  fetch(value, {
    method: "POST",
  })
    .then((response) => response.json())
    .then((responseJson) => {
      console.log(responseJson);
      if (responseJson.hasOwnProperty("token")) {
        pbToken = responseJson.token;
        console.log(pbToken);
        pubnub.setToken(pbToken);
        console.log("Cipher key: " + responseJson.cipher_key);
        pubnub.setCipherKey(responseJson.cipher_key);
        console.log(responseJson.uuid);
        pubnub.setUUID(responseJson.uuid);
        subscribe();
      }
    });
}

function subscribe() {
  console.log("Trying to subscribe with token");
  const channel = pubnub.channel(appChannel);
  const subscription = channel.subscription();
  subscription.subscribe();
}
