import React, { useState, useEffect, useRef } from 'react';
import Typed from 'typed.js';
import { GiHamburgerMenu } from 'react-icons/gi';
import './Chat.css';

const Chat = (props) => {
  const { SecondaryColor, SetSecondaryColor } = props;
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [currentDatetime, setCurrentDatetime] = useState(new Date().toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hour12: true,
  }));
  const [typedKey, setTypedKey] = useState(0);
  const textareaRef = useRef(null);
  let typed = useRef(null);

  useEffect(() => {
    const fetchBotResponse = async () => {
      try {
        const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          mode: 'cors',
          credentials: 'same-origin',
          body: JSON.stringify({ message: 'What is my favorite color?' }),
        });

        if (!response.ok) {
          throw new Error('Failed to communicate with the Rasa server.');
        }

        const responseData = await response.json();
        const botMessages = responseData.map((message) => ({ user: false, text: message.text }));
        SetSecondaryColor((botMessages[0].text).replace(/\s/g, "").toLowerCase());
      } catch (error) {
        console.error(error);
      }
    };

    fetchBotResponse();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDatetime(new Date().toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true,
      }));
      setTypedKey((prevKey) => prevKey + 1);
    }, 60000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    if (typed.current) {
      typed.current.destroy();
    }

    typed.current = new Typed('.datetime', {
      strings: [currentDatetime],
      startDelay: 1800,
      typeSpeed: 30,
      showCursor: false,
    });

    return () => {
      typed.current.destroy();
    };
  }, [currentDatetime]);

  const handleInputChange = (event) => {
    setInputText(event.target.value);
    adjustTextareaHeight();
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '20px';
      if (textareaRef.current.scrollHeight > textareaRef.current.clientHeight) {
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight - 20}px`;
      }
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (inputText.trim() === '' || isSending) return;

    setIsSending(true);

    if (textareaRef.current) {
      textareaRef.current.style.height = '20px';
    }

    const newMessage = { user: true, text: inputText.trim() };
    setMessages([...messages, newMessage]);
    setInputText('');

    try {
      const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        credentials: 'same-origin',
        body: JSON.stringify({ message: inputText.trim() }),
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with the Rasa server.');
      }

      const responseData = await response.json();
      const botMessages = responseData.map((message) => ({ user: false, text: message.text }));

      setTimeout(() => {
        setMessages((prevMessages) => [...prevMessages, ...botMessages]);
        setIsSending(false);
      }, 1000);
    } catch (error) {
      console.error(error);
      setIsSending(false);
    }
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleMenuClick = async (menuItem) => {
    toggleMenu();

    let directInput;
    if (menuItem === "Generating") {
      directInput = 'generate text for me'
    } else if (menuItem === "Summarizing") {
      directInput = 'i need you to summarize something'
    } else if (menuItem === "Paraphrasing") {
      directInput = 'paraphrase text for me'
    } else if (menuItem === "Question Answering") {
      directInput = 'i need you to answer a question from a given text for me'
    }

    const newMessage = { user: true, text: directInput.trim() };
    setMessages([...messages, newMessage]);

    setIsSending(true);

    try {
      const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        credentials: 'same-origin',
        body: JSON.stringify({ message: directInput }),
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with the Rasa server.');
      }

      const responseData = await response.json();
      const botMessages = responseData.map((message) => ({ user: false, text: message.text }));

      setTimeout(() => {
        setMessages((prevMessages) => [...prevMessages, ...botMessages]);
        setIsSending(false);
      }, 1000);
    } catch (error) {
      console.error(error);
      setIsSending(false);
    }
  };

  const renderMessages = () => {
    return messages.map((message, index) => (
      <div key={index} className={message.user ? 'user-message' : 'bot-message'}>
        {message.text}
      </div>
    ));
  };

  return (
    <div className="chat">
      <div className="header">
        <div className="menu" onClick={toggleMenu}>
          <GiHamburgerMenu className="hamburger-icon" />
          {isMenuOpen && (
            <div className="menu-boxes">
              <div className="menu-box" onClick={() => handleMenuClick('Generating')}>
                Generating
              </div>
              <div className="menu-box" onClick={() => handleMenuClick('Summarizing')}>
                Summarizing
              </div>
              <div className="menu-box" onClick={() => handleMenuClick('Paraphrasing')}>
                Paraphrasing
              </div>
              <div className="menu-box" onClick={() => handleMenuClick('Question Answering')}>
                Question Answering
              </div>
            </div>
          )}
        </div>
        <div className="datetime"></div>
      </div>
      <div className="chat-area">
        {renderMessages()}
        {isSending && (
          <div className="bot-message">
            <div className="typing-indicator">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="input-area">
        <textarea
          ref={textareaRef}
          type="text"
          value={inputText}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="input-text textarea"
          disabled={isSending}
        />
        <button type="submit" className="submit-button" style={{ '--secondary-color': SecondaryColor }} disabled={isSending}>
          Submit
        </button>
      </form>
    </div>
  );
};

export default Chat;
