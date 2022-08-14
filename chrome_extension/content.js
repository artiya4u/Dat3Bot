// const BASE_API_URL = "http://127.0.0.1:8000";
// Or
const BASE_API_URL = "https://vision.bootlegsoft.com";

function swipe(action) {
    let bnts = document.querySelectorAll('button.button');
    let swipeButtons = [];
    for (const bnt of bnts) {
        if (['REWIND', 'NOPE', 'SUPER LIKE', 'LIKE', 'BOOST'].includes(bnt.innerText)) {
            swipeButtons.push(bnt);
        }
    }
    if (swipeButtons.length !== 5) {
        // Not found buttons.
        return;
    }
    if (action === 'super-like') {
        console.log('⭐ Send Super Like!');
        let noSuperLike = swipeButtons[2].parentNode.parentNode.querySelectorAll("span[aria-label=\"0 remaining\"]");
        if (noSuperLike.length === 1) {
            // No super like, send like
            swipeButtons[3].click();
        } else {
            // Send super like
            swipeButtons[2].click();
        }
    } else if (action === 'like') {
        console.log('💗 Send Like!');
        swipeButtons[3].click();
    } else { // pass
        console.log('❌ Send Pass');
        swipeButtons[1].click();
    }

    // If popup
    setTimeout(function () {
        let bntsPopup = document.querySelectorAll('button.button');
        for (const bntPop of bntsPopup) {
            // Close Popup -- No, Thanks
            if (bntPop.innerText === 'NO THANKS') {
                console.log('❌ Close Popup');
                bntPop.click();
            }
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

function saveProfile(profile) {
    let headers = new Headers();
    headers.append("Content-Type", "application/json");
    let payload = {
        "name": profile.name ?? '',
        "age": profile.age ?? null,
        "verified": profile.verified ?? false,
        "livesIn": profile.livesIn ?? '',
        "bio": profile.bio ?? '',
        "job": profile.job ?? '',
        "school": profile.school ?? '',
        "passions": profile.passions ?? [],
        "lifeStyles": profile.lifeStyles ?? [],
        "photoUrls": profile.photoUrls ?? [],
    }
    let raw = JSON.stringify(payload);
    let requestOptions = {
        method: 'POST', headers: headers, body: raw, redirect: 'follow'
    };

    return fetch(BASE_API_URL + '/save', requestOptions).then(response => response.json());
}


function findPhotos() {
    let photos = [];
    try {
        let images = document.querySelectorAll('div.StretchedBox[role="img"]');
        for (const imageNode of images) {
            let hide = imageNode.parentNode.parentNode.parentNode.parentNode.getAttribute('aria-hidden');
            if (hide === 'false') { // Displaying profile's image
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

function getValueBySelector(parent, selector) {
    let valueNode = parent.querySelector(selector)
    if (valueNode !== null) {
        return valueNode.innerText;
    }
    return null;
}

function findInfo(profile) {
    try {
        // let nameNode = document.querySelectorAll('span[itemprop="name"]')[1];
        let names = document.querySelectorAll('span[itemprop="name"]');
        for (const nameNode of names) {
            let parent = nameNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode;
            let hide = parent.getAttribute('aria-hidden');
            if (hide === 'false') { // Active profile
                profile.name = nameNode.innerText;

                let age = getValueBySelector(parent, 'span[itemprop="age"]');
                if (age !== null) {
                    profile.age = age;
                }

                let livingIn = getValueBySelector(parent, 'div[itemprop="homeLocation"]');
                if (livingIn != null) {
                    profile.livingIn = livingIn.replace("Lives in ", "");
                }

                let school = getValueBySelector(parent, 'div[itemprop="affiliation"]');
                if (school != null) {
                    profile.school = school.replace("Also went to ", "");
                }

                let job = getValueBySelector(parent, 'div[itemprop="jobTitle"]');
                if (job != null) {
                    profile.job = job;
                }

                let bio = getValueBySelector(parent, '.BreakWord');
                if (bio != null && bio !== '') {
                    profile.bio = bio;
                }

                let titleNode = nameNode.parentNode.parentNode
                let verified = titleNode.querySelector('svg')
                if (verified != null) {
                    profile.verified = true;
                }

                let bubbles = parent.querySelectorAll('div[tabindex="-1"]')
                if (bubbles.length > 0) {
                    let lists = [];
                    for (const bubble of bubbles) {
                        lists.push(bubble.innerText);
                    }
                    if (profile.passions === undefined) {
                        profile.passions = lists;
                    } else if (profile.lifeStyles === undefined) {
                        if (lists.toString() !== profile.passions.toString()) {
                            profile.lifeStyles = lists;
                        }
                    }
                }
            }
        }
    } catch (e) {
        console.log(e);
    }
}

const sleep = async (secs) => new Promise(resolve => setTimeout(resolve, secs * 1000));


async function swipeLoop() {
    while (true) {
        if (Math.random() >= 0.99) {
            location.reload();
        } else {
            try {
                let profile = {};
                findInfo(profile);

                const allPhotos = new Set();

                for (let i = 0; i < 8; i++) { // Browse photos
                    findInfo(profile);
                    let photos = findPhotos();
                    for (const photo of photos) {
                        allPhotos.add(photo);
                    }
                    if (i > 3 && (i - allPhotos.size) >= 0) { // No more photos
                        break;
                    }
                    await sleep(0.5);
                    nextPhoto();
                }
                profile.photoUrls = Array.from(allPhotos);
                console.log(profile);
                console.log('Photos Count', allPhotos.size);
                if (allPhotos.size > 0) { // Must have photos to swipe
                    await saveProfile(profile);
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
                    swipe('pass');
                }
            } catch (e) {
                console.log(e);
            }
        }
        await sleep(0.5 + Math.random());
    }
}

swipeLoop().then();
