const BASE_API_URL = "http://127.0.0.1:8000";

function swipe(action) {
    let bnts = document.querySelectorAll('button.button');
    if (bnts.length !== 5) {
        // Not found buttons.
        return;
    }
    if (action === 'super-like') {
        console.log('⭐ Send Super Like!');
        let noSuperLike = bnts[2].parentNode.parentNode.querySelectorAll("span[aria-label=\"0 remaining\"]");
        if (noSuperLike.length === 1) {
            // No super like, send like
            bnts[3].click();
        } else {
            // Send super like
            bnts[2].click();
        }
    } else if (action === 'like') {
        console.log('💗 Send Like!');
        bnts[3].click();
    } else { // pass
        console.log('❌ Send Pass');
        bnts[1].click();
    }

    // If popup
    setTimeout(function () {
        let bntsPopup = document.querySelectorAll('button.button');
        if (bntsPopup.length > 5) {
            // Close Popup -- No, Thanks
            bntsPopup[bntsPopup.length - 1].click();
        }
    }, 1500);
}

function nextPhoto() { // Browse next photo for active button.
    let activeBullets = document.querySelectorAll("button.bullet.bullet--active");
    for (let activeBullet of activeBullets) {
        let bullet = activeBullet.nextSibling;
        if (bullet !== null) {
            bullet.click();
        } else {
            bullet = activeBullet.parentNode.firstChild;
            if (bullet !== null) {
                bullet.click();
            }
        }
    }
}

function requestCheckImage(profileImageURL) {
    let headers = new Headers();
    headers.append("Content-Type", "application/json");

    let data = {
        url: profileImageURL
    };

    let raw = JSON.stringify(data);
    let requestOptions = {
        method: 'POST', headers: headers, body: raw, redirect: 'follow'
    };

    return fetch(BASE_API_URL + '/check', requestOptions).then(response => response.json());
}


async function findPhotos() {
    let photos = [];
    try {
        let images = document.querySelectorAll('div.StretchedBox[role="img"]');
        for (const imageNode of images) {
            let hide = imageNode.parentNode.parentNode.parentNode.parentNode.getAttribute('aria-hidden');
            if (hide === 'false') { // Displaying profile's image
                // Do something with the image
                let imgUrl = imageNode.style.backgroundImage;
                imgUrl = imgUrl.substring(imgUrl.indexOf("\"") + 1, imgUrl.lastIndexOf("\""));
                photos.push(imgUrl);
            }
        }
        return photos;
    } catch (e) {
        return photos;
    }
}

async function sleep(secs) {
    let requestOptions = {
        method: 'GET',
        redirect: 'follow'
    };

    return fetch(BASE_API_URL + '/sleep?secs=' + secs, requestOptions).then(response => response.json());
}

const psleep = async (secs) => new Promise(resolve => setTimeout(resolve, secs * 1000));

async function swipeLoop() {
    while (true) {
        if (Math.random() >= 0.99) {
            // reload
            // location.reload();
        } else {
            const allPhotos = new Set();
            for (let i = 0; i < 8; i++) { // Browse photos
                let photos = await findPhotos();
                for (const photo of photos) {
                    allPhotos.add(photo);
                }
                await psleep(0.5 + Math.random());
                nextPhoto();
            }
            console.log(allPhotos.size);
            let action = 'pass';
            for (const photo of allPhotos) {
                let result = await requestCheckImage(photo);
                if (result.code === 'OK') {
                    if (result.result === 'HOT') {
                        console.log('😍 HOT!', photo);
                        action = 'like';
                        break;
                    }
                }
            }
            if (action === 'like') {
                console.log('😍 HOT!');
                swipe('pass');
            } else {
                console.log('😵 NOT!');
                swipe('pass');
            }
        }
        await psleep(0.5 + Math.random());
    }
}

swipeLoop().then();