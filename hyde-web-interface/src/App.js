import React, { useState } from 'react';
import Background from './Components/Background/Background';
import Setup from './Scenes/Setup/Setup';
import Chat from './Scenes/Chat/Chat';
import './App.css';

function App() {
  const [secondaryColor, setSecondaryColor] = useState('purple');
  const [enterSetup, setEnterSetup] = useState(true);

  return (
    <div className="App">
      <Background SecondaryColor={secondaryColor} SetSecondaryColor={setSecondaryColor} EnterSetup={enterSetup} >
        {
          enterSetup 
            ? <Setup SetSecondaryColor={setSecondaryColor} SetEnterSetup={setEnterSetup} /> 
            : <Chat SecondaryColor={secondaryColor} SetSecondaryColor={setSecondaryColor} />
        }
      </Background>
    </div>
  );
}

export default App;
