const Applet = imports.ui.applet;
const Mainloop = imports.mainloop;
const St = imports.gi.St;
imports.gi.versions.Soup = '3.0';
const Soup = imports.gi.Soup;
const GLib = imports.gi.GLib;
const PopupMenu = imports.ui.popupMenu;

const SERVER = 'ws://172.16.32.19:8765';
const RECONNECT_SECONDS = 30;

class CommsApplet extends Applet.TextApplet {
    constructor(metadata, orientation, panel_height, instance_id) {
        super(orientation, panel_height, instance_id);
        this.set_applet_label("Comms (X) ");
        this.set_applet_tooltip("Click to Open Comms ");

        //The actual menu 
        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);
        this.logItem = new PopupMenu.PopupMenuItem("No messages yet", { reactive: false });
        this.menu.addMenuItem(this.logItem);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._entry = new St.Entry({ hint_text: "", can_focus: true });
        this.menu.box.add(this._entry);
        let sendItem = new PopupMenu.PopupMenuItem("Send");
        sendItem.connect('activate', () => this._send());
        this.menu.addMenuItem(sendItem);

        this._ws = null;
        this._connect();
    }

    _connect() {
        this.set_applet_label("Comms: ...");
        this.session = new Soup.Session();
        let message = Soup.Message.new('GET', SERVER);
        this.session.websocket_connect_async(message, null, null, null, null, (session, res) => {
            try {
                this._ws = session.websocket_connect_finish(res);
                this.set_applet_label("Comms (●) ");

                this._ws.connect('message', (conn, type, data) => {
                let text = new TextDecoder().decode(data.get_data());    
                if (this.logItem.label.get_text() === "No messages yet") {
                    this.logItem.label.set_text(text);
                } else {           
                    this.logItem.label.set_text(this.logItem.label.get_text() + "\n" + text);
                }
                    this.set_applet_label(`Comms (●): ${text.substring(0, 20)}`);
                });

                this._ws.connect('closed', () => {
                    this.set_applet_label("Comms (X) ");
                    this._scheduleReconnect();
                });
            } catch (e) {
                this.set_applet_label("Comms (X) ");
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
        let text = this._entry.get_text().trim();
        if (text && this._ws) {
            this._ws.send_text(text);
            this._entry.set_text("");
        }
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
