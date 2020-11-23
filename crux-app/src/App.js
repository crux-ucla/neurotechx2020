import React, { useEffect, useState } from 'react';
import { VictoryAxis, VictoryBar, VictoryChart, VictoryLabel } from 'victory';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container'

const API_URL = "http://localhost:8010/proxy/test/"
const ALPHA_URL = API_URL + "alpha";
const BETA_URL = API_URL + "beta";
const ASYMMETRY_URL = API_URL + "alphaAsymmetry";

function App() {
  const [alphaPercentChange, setAlphaPercentChange] = useState(0);
  const [betaPercentChange, setBetaPercentChange] = useState(15);
  const [alphaAsymmetry, setAlphaAsymmetry] = useState(-10);

  const [percentChangeData, setPercentChangeData] = useState( 
    [ 
      {type: -0.25, percentChange: 0},
      {type: 0.25, percentChange: 0}
    ]
  );
  const [asymmetryData, setAsymmetryData] = useState(
    [
      {type: 1, val: 0}
    ]
  );

  useEffect(() => {
    async function getAlphaPercentChange() {
      let response = await fetch(ALPHA_URL, {
        method: 'GET'
      });
      response = await response.json();
      setAlphaPercentChange(parseFloat(response.value));
    }

    async function getBetaPercentChange() {
      let response = await fetch(BETA_URL, {
        method: 'GET'
      });
      response = await response.json();
      setBetaPercentChange(parseFloat(response.value));
    }
    
    const interval = setInterval(() => {
      getAlphaPercentChange();
      getBetaPercentChange();
      setPercentChangeData(
        [ 
          {type: -0.25, percentChange: alphaPercentChange},
          {type: 0.25, percentChange: betaPercentChange}
        ]
      )
    }, 500);
    
    return () => clearInterval(interval);
  }, [alphaPercentChange, betaPercentChange]);

  useEffect(() => {
    async function getAlphaAsymmetry() {
      let response = await fetch(ASYMMETRY_URL, {
        method: 'GET'
      });
      response = await response.json();
      setAlphaAsymmetry(parseFloat(response.value));
    }
    
    const interval = setInterval(() => {
      getAlphaAsymmetry();
      setAsymmetryData(
        [
          {type: 1, val: alphaAsymmetry}
        ]
      )
    }, 500);
    
    return () => clearInterval(interval);
  }, [alphaAsymmetry]);

  return (
    <Container fluid>
      <Row>
        <Col/>
        <Col>
          <VictoryChart maxDomain={{ x: 0.5, y: 150 }} minDomain={{ x: -0.5, y: -150 }}>
          <VictoryLabel 
            text='Percent Change in Power from Baseline' 
            x={225}
            y={20}
            textAnchor='middle'
          />
          <VictoryAxis tickFormat={() => ''}/>
          <VictoryAxis dependentAxis tickFormat={() => ''}/>
          <VictoryBar
            data={percentChangeData}
            x={'type'}
            y={'percentChange'}
            barRatio={1}
            labels={ ({ datum }) => datum.type < 0 ? `alpha: ${datum.percentChange}%` : `beta: ${datum.percentChange}%` }
            style={{
              data: { fill: ({ datum }) => datum.type < 0 ? 'blue' : 'red' }
            }}
          />
          </VictoryChart>
        </Col>
        <Col/>
      </Row>
      <Row>
        <Col/>
        <Col>
          <VictoryChart minDomain={{ y: -2 }} maxDomain={{ y: 2 }}>
          <VictoryLabel
            text='Alpha Asymmetry (Left - Right)'
            x={225}
            y={20}
            textAnchor='middle'
          />
          <VictoryAxis tickFormat={() => ''}/>
          <VictoryAxis dependentAxis tickFormat={() => ''}/>
          <VictoryBar horizontal
            data={asymmetryData}
            x={'type'}
            y={'val'}
            barWidth={100}
            labels={ ({ datum }) => `${datum.val}` }
            style={{
              data: { fill: ['blue'] }
            }}
          />
          </VictoryChart>
        </Col>
        <Col/>
      </Row>
    </Container>
  );
}

export default App;
