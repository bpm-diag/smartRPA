'use strict;'


const clipboardy = require('./clipboardy.js'),
    events = require('events'),
    eventEmitter = new events.EventEmitter();

//watch board
var content, stop = false;

function watch(interval) {

    //start the watcher...
    readClip(interval);

    return Object.assign(eventEmitter, {
        end: function () {
            stop = true;
        }
    });
}

function readClip(interval) {
    var self = this;

    self.interval = self.interval || (Number(interval) || 500);
    var abc=true;
    clipboardy.read()
        .then(function (data) {
            //console.log(data)
            //emit copy event if clipboard content changes
            if (data !== content) {
                eventEmitter.emit('copy', data);
                content = data;
            }

            var timeout = setTimeout(function () {
                //clear timeout
                clearTimeout(timeout);  
                
                if(!stop){
                    //recall self
                    process.nextTick(readClip);
                }
               

            }, self.interval);

        })
        .catch(function (err) {
            throw err;
        });

}

//exports
module.exports = watch;