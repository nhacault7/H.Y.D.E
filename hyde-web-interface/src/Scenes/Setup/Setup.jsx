import React, { useState } from 'react';
import Typed from 'react-typed';
import { BsArrowRight } from 'react-icons/bs';
import './Setup.css';

const Setup = (props) => {
  const { SetSecondaryColor, SetEnterSetup } = props;
  const [storySteps, setStorySteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkColor, setCheckColor] = useState(false);

  const triggerSetupStory = async () => {
    try {
      const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'same-origin',
        body: JSON.stringify({ message: 'setup enter' }),
      });

      const responseData = await response.json();

      if (responseData) {
        const steps = responseData.map((message) => {
          const step = { type: 'text', content: message.text };

          if (message.buttons && Array.isArray(message.buttons)) {
            step.buttons = message.buttons;
            step.type = 'buttons';
          }

          return step;
        });

        setStorySteps(steps);
        setLoading(false);
      }
    } catch (error) {
      console.log('connection timeout, retrying in 5 seconds');
      setTimeout(triggerSetupStory, 5000);
    }
  };

  const validateColor = (e) => {
    e.preventDefault();

    const namedColors = [
      "aliceblue",
      "antiquewhite",
      "aqua",
      "aquamarine",
      "azure",
      "beige",
      "bisque",
      "blanchedalmond",
      "blue",
      "blueviolet",
      "brown",
      "burlywood",
      "cadetblue",
      "chartreuse",
      "chocolate",
      "coral",
      "cornflowerblue",
      "cornsilk",
      "crimson",
      "cyan",
      "darkblue",
      "darkcyan",
      "darkgoldenrod",
      "darkgray",
      "darkgreen",
      "darkgrey",
      "darkkhaki",
      "darkmagenta",
      "darkolivegreen",
      "darkorange",
      "darkorchid",
      "darkred",
      "darksalmon",
      "darkseagreen",
      "darkslateblue",
      "darkslategray",
      "darkslategrey",
      "darkturquoise",
      "darkviolet",
      "deeppink",
      "deepskyblue",
      "dimgray",
      "dimgrey",
      "dodgerblue",
      "firebrick",
      "floralwhite",
      "forestgreen",
      "fuchsia",
      "gainsboro",
      "ghostwhite",
      "gold",
      "goldenrod",
      "gray",
      "green",
      "greenyellow",
      "grey",
      "honeydew",
      "hotpink",
      "indianred",
      "indigo",
      "ivory",
      "khaki",
      "lavender",
      "lavenderblush",
      "lawngreen",
      "lemonchiffon",
      "lightblue",
      "lightcoral",
      "lightcyan",
      "lightgoldenrodyellow",
      "lightgray",
      "lightgreen",
      "lightgrey",
      "lightpink",
      "lightsalmon",
      "lightseagreen",
      "lightskyblue",
      "lightslategray",
      "lightslategrey",
      "lightsteelblue",
      "lightyellow",
      "lime",
      "limegreen",
      "linen",
      "magenta",
      "maroon",
      "mediumaquamarine",
      "mediumblue",
      "mediumorchid",
      "mediumpurple",
      "mediumseagreen",
      "mediumslateblue",
      "mediumspringgreen",
      "mediumturquoise",
      "mediumvioletred",
      "midnightblue",
      "mintcream",
      "mistyrose",
      "moccasin",
      "navajowhite",
      "navy",
      "oldlace",
      "olive",
      "olivedrab",
      "orange",
      "orangered",
      "orchid",
      "palegoldenrod",
      "palegreen",
      "paleturquoise",
      "palevioletred",
      "papayawhip",
      "peachpuff",
      "peru",
      "pink",
      "plum",
      "powderblue",
      "purple",
      "rebeccapurple",
      "red",
      "rosybrown",
      "royalblue",
      "saddlebrown",
      "salmon",
      "sandybrown",
      "seagreen",
      "seashell",
      "sienna",
      "silver",
      "skyblue",
      "slateblue",
      "slategray",
      "slategrey",
      "snow",
      "springgreen",
      "steelblue",
      "tan",
      "teal",
      "thistle",
      "tomato",
      "turquoise",
      "violet",
      "wheat",
      "whitesmoke",
      "yellow",
      "yellowgreen"
    ];

    if (namedColors.includes((e.target.elements.textInput.value).replace(/\s/g, "").toLowerCase())) {
      handleTextResponse(e);
    }
  };

  const handleButtonResponse = async (e, responsePayload) => {
    if (responsePayload.message === 'setup finish') {
      SetEnterSetup(false);
      return;
    }
    
    // Hide the button input immediately
    const btn = document.querySelector('.next-button');
    btn.classList.add('hidden');

    try {
      const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'same-origin',
        body: JSON.stringify(responsePayload),
      });

      const responseData = await response.json();

      if (responseData) {
        const steps = responseData.map((message) => {
          const step = { type: 'text', content: message.text };

          if (message.buttons && Array.isArray(message.buttons)) {
            step.buttons = message.buttons;
            step.type = 'buttons';
          }

          return step;
        });

        if (responsePayload.message === 'setup user') {
          const btn = document.querySelector('.input-container');
          btn.classList.remove('hidden');
        }

        setStorySteps((prevSteps) => [...prevSteps, ...steps]);
      }
    } catch (error) {
      console.error('Error handling user response:', error);
    }
  };

  const handleTextResponse = async (e) => {
    e.preventDefault();
  
    if (checkColor) {
      SetSecondaryColor((e.target.elements.textInput.value).replace(/\s/g, "").toLowerCase());
      setCheckColor(false);
    }
  
    // Hide the text input immediately
    const input = document.querySelector('.input-container');
    input.classList.add('hidden');
  
    try {
      const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'same-origin',
        body: JSON.stringify({ message: e.target.elements.textInput.value }),
      });
  
      const responseData = await response.json();
  
      if (responseData) {
        const steps = responseData.map((message) => {
          const step = { type: 'text', content: message.text };
  
          if (message.buttons && Array.isArray(message.buttons)) {
            step.buttons = message.buttons;
            step.type = 'buttons';
          }
  
          return step;
        });
  
        setStorySteps((prevSteps) => [...prevSteps, ...steps]);
      }
    } catch (error) {
      console.error('Error handling user response:', error);
    }
  };  

  const checkProgress = (step) => {
    if (step.buttons) {
      if (document.querySelector('.next-button').classList.contains('hidden')) {
        document.querySelector('.next-button').classList.remove('hidden');
      }
    } else {
      if (document.querySelector('.input-container').classList.contains('hidden')) {
        document.querySelector('.input-container').classList.remove('hidden');
      }
    }

    if (step.content.includes('color')) {
      setCheckColor(true);
    }
  };

  return (
    <div className="setup-container">
      {storySteps.map((step, index) => (
        index === storySteps.length - 1 && (
          <div key={index} className="step">
            {step.type === 'text' && (
              <div className="texts">
                <Typed
                  strings={[step.content]}
                  typeSpeed={50}
                  showCursor={true}
                  onComplete={() => checkProgress(step)}
                />
              </div>
            )}
            {step.type === 'buttons' && (
              <div className="buttons">
                <Typed
                  strings={[step.content]}
                  typeSpeed={50}
                  showCursor={true}
                  onComplete={() => checkProgress(step)}
                />
              </div>
            )}
            <form className="input-container hidden" onSubmit={(e) => (checkColor ? validateColor(e) : handleTextResponse(e))}>
              <input className="input-field" type="text" name="textInput" />
            </form>
            <div className="next-button hidden" onClick={(e) => handleButtonResponse(e, { message: step.buttons[0].payload })}>
              <div className="circle-button">
                <div className="circle-container circle-container--right">
                  <div className="circle-piece circle-right"></div>
                </div>
                <div className="circle-container circle-container--left">
                  <div className="circle-piece circle-left"></div>
                </div>
              </div>
              <BsArrowRight className="arrow" />
            </div>
          </div>
        )
      ))}
      {loading && (
        <div className="message bot loading">
          <Typed
            strings={['Connecting...']}
            typeSpeed={50}
            showCursor={true}
            onComplete={() => triggerSetupStory()}
          />
        </div>
      )}
    </div>
  );
};

export default Setup;