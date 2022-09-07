import { values } from "lodash";

// The following colors will be used if you pick "Automatic" color
export const BaseColors = {
  "Dark Blue": "#1D4289",
  "Light Blue": "#41B6E6",
  "Dark Green": "#007A78",
  "Light Green": "#94CCC7",
  "Rose": "#BE84A3",
  "Purple": "#5D3754",
  "Yellow": "#FFC845",
  "Orange": "#DC582A",
  "Red": "#D3273E",
  "Beige": "#A8A59A",
  "Black": "#000000",
  "Grey-Blue": "#83A3BF",
  "Sand": "#E2B063",
  "Cyan": "#47DAE5",
};

// Additional colors for the user to choose from
export const AdditionalColors = {
  "Indian Red": "#981717",
  "Green 2": "#17BF51",
  "Green 3": "#049235",
  "Dark Turquoise": "#00B6EB",
  "Dark Violet": "#A58AFF",
  "Pink 2": "#C63FA9",
};

export const ColorPaletteArray = values(BaseColors);

const ColorPalette = {
  ...BaseColors,
  ...AdditionalColors,
};

export default ColorPalette;
