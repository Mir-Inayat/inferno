import React, { useState } from 'react';
import './FeedbackForm.css';

const FeedbackForm = ({ documentId }) => {
    const [rating, setRating] = useState(0);
    const [comment, setComment] = useState('');
    const [message, setMessage] = useState('');
    
    const handleSubmit = (e) => {
        e.preventDefault();
        setMessage('Thank you for your feedback!');
        setRating(0);
        setComment('');
        
        // Hide the success message after 3 seconds
        setTimeout(() => {
            setMessage('');
        }, 3000);
    };
    
    return (
        <form onSubmit={handleSubmit} className="feedback-form">
            <h3>Document Feedback</h3>
            
            <div className="rating-container">
                <div className="star-rating">
                    {[1, 2, 3].map((star) => (
                        <button
                            key={star}
                            type="button"
                            className={`star ${star <= rating ? 'active' : ''}`}
                            onClick={() => setRating(star)}
                        >
                            ★
                        </button>
                    ))}
                </div>
            </div>
            
            <div className="comment-container">
                <textarea
                    placeholder="Add your comments (optional)"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    rows={4}
                />
            </div>
            
            <button
                type="submit"
                className="submit-button"
                disabled={!rating}
            >
                OK
            </button>
            
            {message && (
                <div className="message success">
                    {message}
                </div>
            )}
        </form>
    );
};

export default FeedbackForm;