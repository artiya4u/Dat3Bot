const API_URL = "http://127.0.0.1:8000/check";

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
    console.log('Next photo');
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
        method: 'POST',
        headers: headers,
        body: raw,
        redirect: 'follow'
    };

    return fetch(API_URL, requestOptions).then(response => response.json());
}

const checkedPhotos = new Set();

async function checkPhoto() {
    let images = document.querySelectorAll('div.StretchedBox[role="img"]');
    for (const imageNode of images) {
        let hide = imageNode.parentNode.parentNode.parentNode.parentNode.getAttribute('aria-hidden');
        if (hide === 'false') { // Displaying profile's image
            // Do something with the image
            let imgUrl = imageNode.style.backgroundImage;
            imgUrl = imgUrl.substring(
                imgUrl.indexOf("\"") + 1,
                imgUrl.lastIndexOf("\"")
            );
            console.log(imgUrl);
            if (checkedPhotos.has(imgUrl)) {
                continue;
            }
            checkedPhotos.add(imgUrl);
            let result = await requestCheckImage(imgUrl);
            if (result.code === 'OK') {
                if (result.found === 'HOT') {
                    console.log('🔥 HOT!', imgUrl);
                    swipe('like')
                    return;
                } else {
                    console.log('❌ NOPE!', imgUrl);
                    swipe('pass')
                    return;
                }
            }
            console.log('DONT KNOW!', imgUrl);
            swipe('pass')
        }
    }
}

function swipeLoop() {
    setTimeout(async function () {
        if (Math.random() >= 0.99) {
            // reload
            // location.reload();
        } else {
            await checkPhoto();
        }
        swipeLoop();
    }, 1000);
}

swipeLoop();