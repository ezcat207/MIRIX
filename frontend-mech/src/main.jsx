import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import MechPilot from './MechPilot.jsx'
import './styles/MechPilot.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <MechPilot />
  </StrictMode>,
)
