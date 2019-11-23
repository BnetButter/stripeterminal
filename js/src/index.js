/*Copyright (C) <2019>  <Kevin Lai>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

class Client
{
    constructor(port, ip="localhost")
    {
        this.futures = {}; // stores the result of fetch_connection_token
        this.ws = new WebSocket(`ws://${ip}:${port}`);
                this.ws.onmessage = async (msg) => await this.on_message(msg);
        this.ws.onclose = () => reload(1000);
        this.ws.onerror = () => reload(1000);
        this.terminal = window.StripeTerminal.create({
            onFetchConnectionToken:
                async () => await this.fetch_connection_token(),
            onUnexpectedReaderDisconnect:
                async () => await this.on_unexpected_reader_disconnect()
            });
    }

    
    async on_message(message)
    {

        await wait_for(() => this.ws.readyState)
        message = JSON.parse(message.data);

        /* This statement executes when fetch_connection_token() 
        when a request is sent, handled and returned by the python runtime.*/
        if (message.result)
            return this.futures[message.attribute] = message.result;
        
        
        if (typeof(this.terminal[message.attribute]) == "function") {
        
            /*Execute the requested subroutine and return the results or
            any error that may occur during execution */  
            try {
                let returnvalue = this.terminal[message.attribute](
                    ...message.args, message.kwargs)
                
                if (returnvalue.constructor === Promise)
                    this.ws.send(JSON.stringify(await returnvalue));
                else
                    this.ws.send(JSON.stringify(returnvalue));
            }
            catch (err) {
                console.log(err.code)
                console.debug(`${message}|${err}`)
                this.ws.send(JSON.stringify(
                    {"error": [err.name, err.message]}
                    ));
            }
        }
        else {
            this.ws.send(JSON.stringify(this.terminal[message.attribute]));
        }
    }

    async fetch_connection_token()
    {
        await wait_for(()=>this.ws.readyState)
        this.ws.send(
            JSON.stringify(
                    {
                        attribute:"connection_token",
                        args:[],
                        kwargs:{},
                    }
                ));
        return (await this.get("connection_token")).secret;
        
    }


    async on_unexpected_reader_disconnect()
    {
        this.ws.send(
            JSON.stringify(
                {
                    attribute:"unexpected_reader_disconnect",
                    args:[],
                    kwargs:{}
                }
            ));
        return await this.get("unexpected_reader_disconnect")
    }

    async get(attribute)
    {
        await wait_for(() => this.futures[attribute])
        return this.futures[attribute]
    }
}

function
sleep(ms)
{
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function
wait_for(predicate, interval=50)
{
    while (! predicate())
        await sleep(interval);
}

function
reload(ms)
{
    sleep(ms).then(()=>document.location.reload())
}

new Client(5000)