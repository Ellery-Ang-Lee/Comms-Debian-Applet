const Applet = imports.ui.applet;
const Mainloop = imports.mainloop;
const St = imports.gi.St;
imports.gi.versions.Soup = '3.0';
const Soup = imports.gi.Soup;
const GLib = imports.gi.GLib;
const PopupMenu = imports.ui.popupMenu;

const SERVER = 'wss://172.16.32.19:8765';
const RECONNECT_SECONDS = 10;

let connected = false;

class CommsApplet extends Applet.TextApplet {
    constructor(metadata, orientation, panel_height, instance_id) {
        super(orientation, panel_height, instance_id);
        this.set_applet_label("Comms (-) ");
        this.set_applet_tooltip("Click to Open Comms ");

        //The actual menu 
        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);
        //this.logItem = new PopupMenu.PopupMenuItem("", { reactive: false });
        //this.logItem.label.style_class = "applet-log-item";
        //this.menu.addMenuItem(this.logItem);
        this.logbox = new St.BoxLayout({ vertical: true, style_class: "applet-log-box" });
        this.menu.box.add(this.logbox);
        //this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this.usernameEntry = new St.Entry({ hint_text: "username", can_focus: true, style_class: "applet-entry applet-username-entry" });
        this.menu.box.add(this.usernameEntry);
        this.entry = new St.Entry({ hint_text: "Write a message here...", can_focus: true, style_class: "applet-entry" });
        this.menu.box.add(this.entry);
        let sendItem = new PopupMenu.PopupMenuItem("Send");
        sendItem.connect('activate', (actor, event) => {
            this._send();
            return true; 
        });
        this.menu.addMenuItem(sendItem);

        this._ws = null;
        this._connect();
    }

    _connect() {
        if (connected) {
            return;
        }
        this.set_applet_label("Comms (-): ...");
        if (this.session) {
            this.session.abort();
        }
        this.session = new Soup.Session();
        let message = Soup.Message.new('GET', SERVER);

        this.session.accept_language = null;
        message.connect('accept-certificate', () => true);

        this.session.websocket_connect_async(message, null, null, null, null, (session, res) => {
            try {
                this._ws = session.websocket_connect_finish(res);
                this.set_applet_label("Comms (+) ");
                connected = true;

                this._ws.connect('message', (conn, type, data) => {
                    let msg = JSON.parse(new TextDecoder().decode(data.get_data()));
                    this._appendMessage(msg.text, msg.color, msg.user);
                    this.set_applet_label(`Comms (+): ${msg.text.substring(0, 20)} `);
                });

                this._ws.connect('closed', () => {
                    connected = false;
                    this._ws = null;
                    this.set_applet_label("Comms (-) ");
                    this._scheduleReconnect();
                });
            } catch (e) {
                connected = false;
                this.set_applet_label("Comms (-) ");
                this._scheduleReconnect();
            }
        });
    }

    _scheduleReconnect() {
        Mainloop.timeout_add_seconds(RECONNECT_SECONDS, () => {
            this._connect();
            return false;
        });
    }

    _send() {
        let text = this.entry.get_text().trim();
        let user = this.usernameEntry.get_text().trim() || "anonymous";
        let payload = JSON.stringify({ user: user, text: text, color: "White" });
        if (text && this._ws) {
            this._ws.send_text(payload);
            this.entry.set_text("");
        }
    }

    _appendMessage(text, color, user) {
        let children = this.logbox.get_children();
        if (children.length > 50) {
            this.logbox.remove_child(children[0]);
        }

        let label = new St.Label({ text: user + " - " + text});
        if (user === "SERVER") {
            label.set_style(`color: ${color}; font-size: 12px; text-align: left; white-space: pre-wrap; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;`);
        } else {
            label.set_style(`color: ${color}; font-size: 12px; text-align: left; white-space: pre-wrap; font-family: monospace;`);
        }
        this.logbox.add_child(label);
    }

    on_applet_clicked() {
        this.menu.toggle();
    }

    on_applet_removed_from_panel() {
        if (this._ws) this._ws.close(1000, '');
    }
}

function main(metadata, orientation, panel_height, instance_id) {
    return new CommsApplet(metadata, orientation, panel_height, instance_id);
}
