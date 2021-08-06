// /* globals io */
//
// typeof Notification !== "undefined"
// Notification.permission
// Notification.requestPermission().then(function (permission) {
//     console.log(permission);
// });
function generate_browser_notification(title, icon, body) {
    // var notification = new Notification(title, {body, icon});
    // // notification.close();
}

localStorage.removeItem('currentRoom')


// let showNotification = document.visibilityState !== "visible";
// if(showNotification) {
//    // Notification code
// }
//
// var notification = new Notification('Travel');
// notification.close();

function makeid(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() *
            charactersLength));
    }
    return result;
}

function chatHTML(message, user, timestamp) {
    return `
    <div class="row my-0" id="message-format">
      <div class="col-6">
        <p class="text-left font-weight-light my-0" id="message-timestamp">${timestamp}</p>
      </div>
      <div class="col-6">
        <p class="text-right font-weight-bold my-0" id="message-username">${user}</p>
      </div>
      <div class="col-12">
        <p class="text-right my-0" id="message-text">${message}</p>
      </div>
    </div>`;
}

function select_chat(room_id) {
    localStorage.setItem('currentRoom', room_id)
    document.getElementById('submit-message-input').style.display = "block";
    fetch(`${window.location.protocol}//${document.domain}:${window.location.port}/api/message/?room=${room_id}`)
        .then(response => response.json())
        .then(data => {
            const messages = data.data.messages;
            currentRoom = data.data.room.id;
            currentRoomName = data.data.room.name
            const chatroom = document.querySelector('#messages-list');

            while (chatroom.firstChild) {
                chatroom.removeChild(chatroom.firstChild);
            }
            document.getElementById('submit-message-input-header').innerHTML = 'Current Room: ' + currentRoomName
            messages.forEach(messageItem => {
                // Create the divider element
                const divider = document.createElement('hr');
                divider.className = 'my-1';

                // Append the divider element
                chatroom.appendChild(divider);

                // Extract the timestamp, username, and message
                const {
                    message_body
                } = messageItem;
                const timestamp = messageItem.created_at;
                const user = messageItem.sender.email;

                // Create chat message div
                const div = document.createElement('div');
                div.innerHTML = chatHTML(message_body, user, timestamp); // returns custom HTML string
                chatroom.appendChild(div);

                // Move the scrollbar to the bottom of the chat
                const objDiv = document.getElementById('messages-list');
                objDiv.scrollTop = objDiv.scrollHeight;
            });
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}


document.addEventListener('DOMContentLoaded', () => {
    // Global vars
    let username = null;
    let currentRoom = null;
    if (localStorage.getItem('currentRoom') == null) {
        document.getElementById('submit-message-input').style.display = "none";
    }
    document.getElementById('name_field').innerHTML = localStorage.getItem('name')

    // Hide the chatroom initially
    const form = document.querySelector('#chatroom');
    form.style.display = 'none';

    // Connect to websocket
    const socket = io.connect(`${window.location.protocol}//${document.domain}:${window.location.port}`, (socket) => {
        console.log('dfadfsafs', socket.id)
    });
    socket.emit('get_chats', {
        'user': {
            'user_id': localStorage.getItem('user_id'),
            'email': localStorage.getItem('email'),
            'name': localStorage.getItem('name')
        }
    }, (callback) => {
        console.log('dfs')
    })

    // By default, ensure the login submit button is disabled
    document.querySelector('#login_submit_button').disabled = true;

    // By default, ensure the channel button is disabled
    document.querySelector('#new-channel-button').disabled = true;

    // Enable user submit button only if there is text in the input field
    document.querySelector('#username-input').onkeyup = () => {
        if (document.querySelector('#username-input').value.length > 0)
            document.querySelector('#login_submit_button').disabled = false;
        else document.querySelector('#login_submit_button').disabled = true;
    };

    // Enable new channel button only if there is text in the input field
    document.querySelector('#new-channel-input').onkeyup = () => {
        if (document.querySelector('#new-channel-input').value.length > 0)
            document.querySelector('#new-channel-button').disabled = false;
        else document.querySelector('#new-channel-button').disabled = true;
    };

    // Define the unhide chatroom function
    function unhideChatroom() {
        // Unhide the chatroom
        const chatroom = document.querySelector('#chatroom');
        chatroom.style.display = 'block';

        // Hide the user submission form
        const div = document.querySelector('#user-submission-div');
        div.style.display = 'none';

        // Show the username in index.html
        document.querySelector('#hello-user').innerHTML = username;
    }


    // When connected, configure submission forms and buttons
    socket.on('connect', () => {
        // ? When the username is submitted
        socket.emit('connected', {
            user: {
                'user_id': localStorage.getItem('user_id'),
                'email': localStorage.getItem('email'),
                'name': localStorage.getItem('name')
            },
            'sid': socket.io.engine.id
        });

        console.log(socket)
        document.querySelector('#new-user-form').onsubmit = () => {
            // Grab the username from the input field
            const name = document.querySelector('#username-input').value;
            const email = document.querySelector('#email-input').value;
            localStorage.setItem('name', name)
            localStorage.setItem('email', email)
            localStorage.setItem('user_id', makeid(10))
            location.reload();
            return false;
        };

        // ? If the username is already set in local storage
        if (localStorage.getItem('user_id')) {
            // Unhide chatroom
            unhideChatroom();

            // Verify the local storage channel name first
            socket.emit('verify channel', {
                channel: currentRoom
            });

            // Store username and current channel
            username = localStorage.getItem('username');
            currentRoom = localStorage.getItem('currentRoom');

            // Show the username in index.html
            document.querySelector('#hello-user').innerHTML = username;

            // Check with the server that this 'username' is accounted for
            socket.emit('confirm login', {
                username
            });

            // Move the user to the saved channel
            socket.emit('move to channel', {
                channel: currentRoom
            });
        }

        // ? Configure the Create channel form
        document.querySelector('#new-channel-form').onsubmit = () => {

            console.log('dfasldkfjdlskjl')
            // Add the channel name to the local vars in this function
            const channel = document.querySelector('#new-channel-input').value;

            // Clear the input field and disable the button again
            document.querySelector('#new-channel-input').value = '';
            document.querySelector('#new-channel-button').disabled = true;
            data = {
                name: channel,
                participants: [{
                    'user_id': '61010d7ce4c9786a417b4113',
                    'email': 'nitesh.kumar+1@techstriker.com',
                    'name': 'Ravi'
                }],
                user: {
                    'user_id': localStorage.getItem('user_id'),
                    'email': localStorage.getItem('email'),
                    'name': localStorage.getItem('name')
                },
                is_group: true
            }
            // Broadcast the channel creation to the server
            socket.emit('new_room_create', data);

            // Stop form from refreshing
            return false;
        };

        // ? Configure the send message form
        document.querySelector('#submit-message-form').onsubmit = () => {
            // Grab the message
            const message = document.querySelector('#submit-message-input').value;

            // Clear the input field
            document.querySelector('#submit-message-input').value = '';
            // Broadcast the message AND channel to the server
            socket.emit('new_message', {
                room: localStorage.getItem('currentRoom'),
                message_body: message,
                type: 'USER_TEXT_MESSAGE',
                user: {
                    'user_id': localStorage.getItem('user_id'),
                    'email': localStorage.getItem('email'),
                    'name': localStorage.getItem('name')
                },
            });

            // Prevent the submission from refreshing
            return false;
        };
    });

    // ? If channel name fails, throw up an alert
    socket.on('room_creation_failed', () => {
        alert('Channel already exists. Try another name.');
    });

    socket.on('set_chats', data => {
        html = ''
        console.log(data)
        for (let d of data['chats']) {
            id = d['id']
            html += `<button class="btn btn-secondary" id="${d['id']}" name="channel-button" onclick="select_chat('${id.toString()}')" type="submit">${d['name']}</button>`
        }
        document.getElementById('channel-button-list').innerHTML = html
    })

    // ? If channel name was successful
    socket.on('add_room', data => {
        // Grab the channel name added, uses object destructuring
        const {
            channel
        } = data;
                debugger;

        // Create the button for the channel
        console.log('dfaljdlkfsaklfjlksfkl;jsdl')
        const button = document.createElement('button');
        button.className = 'btn btn-secondary';
        button.id = channel.id;
        button.innerHTML = channel.name;
        button.name = 'channel-button'

        button.setAttribute('onclick', `select_chat("${channel.id}")`)

        // Add the button to the channel list
        document.querySelector('#channel-button-list').append(button);
    });

    // ? If the username is already taken
    socket.on('username taken', () => {
        // Alert the user that the name is taken
        document.querySelector('#username-taken').innerHTML =
            '<i class="my-0">Username taken!</i>';
    });


    socket.on('message_broadcast', data => {
        // Set variable
        console.log('message broadcast', data)
        const {
            message_body
        } = data.message_body;
        const {
            room
        } = data;
        const {
            timestamp
        } = data;
        const user = data.sender.email;
        const chatroom = document.querySelector('#messages-list');

        // Check if the user is in the channel (whether they should see the message)
        generate_browser_notification(title = 'New Message: ' + message_body, body = message_body)
        if (localStorage.getItem('currentRoom') === room) {
            // Create the divider element
            const divider = document.createElement('hr');
            divider.className = 'my-1';

            // Append the divider element
            chatroom.appendChild(divider);

            // Create chat message div
            const div = document.createElement('div');
            div.innerHTML = chatHTML(message_body, user, timestamp); // returns custom-made string
            chatroom.appendChild(div);

            // Move the scrollbar to the bottom of the chat
            const objDiv = document.getElementById('messages-list');
            objDiv.scrollTop = objDiv.scrollHeight;

        }
    });

    // ? Handle invalid channel name with a prompt
    socket.on('invalid channel name', () => {
        alert('Invalid channel name!');
    });

    // ? Default channel name
    socket.on('default channel', () => {
        currentRoom = 'Main Channel';
    });
});