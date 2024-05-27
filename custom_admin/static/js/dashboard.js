/**
 * Deletes a post by sending a DELETE request to the server.
 * 
 * @param {string} postId - The ID of the post to be deleted.
 * @returns {Promise} - A promise that resolves with the response data.
 * @throws {Error} - If there is an error during the request.
 */
function deletePost(postId) {
    fetch(`/custom_admin/delete-reported-post/${postId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.message || data.error) {
                const popup = createPopup(data.message || data.error);
                document.body.appendChild(popup);

                const closeButton = document.createElement('button');
                closeButton.textContent = 'Close';
                closeButton.addEventListener('click', () => {
                    popup.remove();
                    window.location.reload();
                });
                popup.appendChild(closeButton);

                setTimeout(() => {
                    popup.remove();
                    window.location.reload();
                }, 3000);
            } else {
                console.error('Error:', error);
            }
            return response.json();
        })
        .catch(error => console.error('Error:', error));
}

/**
 * Creates a popup element with the given message.
 * 
 * @param {string} message - The message to be displayed in the popup.
 * @returns {HTMLElement} - The created popup element.
 */
function createPopup(message) {
    const popup = document.createElement('div');
    popup.classList.add('custom-popup');
    popup.innerHTML = message;
    return popup;
}


