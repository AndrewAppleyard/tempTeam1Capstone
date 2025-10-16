import { createVuetify } from 'vuetify'
import 'vuetify/styles'

const myCustomLightTheme = {
  dark: false,
  colors: {
    background: '#E5F3FD',     
    surface: '#FFFFFF',        // default card color (override)
    primary: '#002856',        
    secondary: '#9ABDDC',      // light blue for cards
    cardOutline: '#002856',    
  }
}

export default createVuetify({
  theme: {
    defaultTheme: 'myCustomLightTheme',
    themes: {
      myCustomLightTheme,
    },
  },
})
