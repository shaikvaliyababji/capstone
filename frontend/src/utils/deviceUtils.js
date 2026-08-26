import { 
  Lightbulb, 
  Wind, 
  Snowflake, 
  Tv, 
  Plug, 
  Activity, 
  Cpu,
  Lock,
  Sliders
} from 'lucide-react';

/**
 * Format snake_case device names into Title Case.
 * Example: "bedroom_light" -> "Bedroom Light"
 * @param {string} name 
 * @returns {string}
 */
export function formatDeviceName(name) {
  if (!name) return '';
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Get the appropriate Lucide React icon component based on device category.
 * @param {string} category 
 * @returns {React.ComponentType}
 */
export function getDeviceIcon(category) {
  const cat = (category || '').toLowerCase();
  switch (cat) {
    case 'light':
      return Lightbulb;
    case 'fan':
      return Wind;
    case 'ac':
    case 'air_conditioner':
      return Snowflake;
    case 'tv':
    case 'television':
      return Tv;
    case 'plug':
    case 'outlet':
      return Plug;
    case 'sensor':
      return Activity;
    case 'security':
      return Lock;
    case 'comfort':
      return Sliders;
    default:
      return Cpu;
  }
}
