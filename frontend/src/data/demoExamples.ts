export interface DemoExample {
  label: string;
  factPattern: string;
  argument: string;
}

export const demoExamples: DemoExample[] = [
  {
    label: "Defective Work Claim",
    factPattern:
      "Objednatel si u dodavatele objednal rekonstrukci koupelny. Dílo bylo předáno 1. 3. 2024. " +
      "Objednatel zjistil netěsnost sprchového koutu dne 20. 8. 2024 a reklamoval ji dopisem ze dne " +
      "25. 8. 2024. Dodavatel reklamaci odmítl s odkazem na opožděné oznámení vady.",
    argument:
      "Jako objednatel tvrdím, že jsem vadu oznámil bez zbytečného odkladu poté, co se projevila, a " +
      "mám nárok na bezplatné odstranění vady dle § 2586 a násl. občanského zákoníku. Vada nebyla " +
      "zjevná při předání díla a projevila se až po několika měsících užívání.",
  },
  {
    label: "Wrongful Termination",
    factPattern:
      "Zaměstnanci byla dána výpověď pro nadbytečnost dle § 52 písm. c) zákoníku práce s odůvodněním " +
      "organizační změny. Zaměstnanec tvrdí, že na jeho místo byl do 14 dnů přijat nový pracovník na " +
      "stejnou pozici.",
    argument:
      "Jako zaměstnanec tvrdím, že výpověď je neplatná, protože organizační změna byla pouze účelová " +
      "a fiktivní — moje pracovní místo fakticky nezaniklo, jelikož zaměstnavatel na stejnou pozici " +
      "téměř okamžitě přijal jinou osobu.",
  },
];
