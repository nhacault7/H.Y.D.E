import React, { useEffect } from 'react';
import './Background.css';

const Background = (props) => {
  const { SecondaryColor, SetSecondaryColor, EnterSetup, children } = props;
  const Color = require('color');

  useEffect(() => {
    const userDefinedColor = Color(SecondaryColor);

    const userColor = `rgba(${userDefinedColor.red()}, ${userDefinedColor.green()}, ${userDefinedColor.blue()}, 0.6)`;

    if (EnterSetup) {
      console.log(document.querySelector('.background-container').classList.add('breath'))
    }
    else {
      document.querySelector('.background-container').classList.remove('breath')
    }

    SetSecondaryColor(userColor);
  }, [SecondaryColor, EnterSetup]);

  return (
    <div className="background-container" style={{ '--secondary-color': SecondaryColor }}>
      {children}
    </div>
  );
};
  
export default Background;