<?php
// Phoenix Rebirth | Numerology Calculator
// Proprietary — Christina Stevens
// Sequential A=1 through Z=26 — no reduction on letter values
// Master numbers NEVER reduced. Ever.

function _num_letter_values() {
    $vals = array();
    $alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    for ($i = 0; $i < 26; $i++) {
        $vals[$alpha[$i]] = $i + 1;
    }
    return $vals;
}

function _num_vowels() {
    return array('A', 'E', 'I', 'O', 'U');
}

function numerology_is_master($n) {
    return in_array(intval($n), array(11, 22, 33, 44, 55, 66, 77, 88, 99, 111, 222, 333), true);
}

function numerology_is_karmic($n) {
    return in_array(intval($n), array(13, 14, 16, 19), true);
}

function numerology_reduce($n) {
    $n = intval($n);
    if (numerology_is_master($n)) return $n;
    if ($n < 10) return $n;
    $sum = 0;
    foreach (str_split((string)$n) as $d) $sum += intval($d);
    if (numerology_is_master($sum)) return $sum;
    if ($sum >= 10) return numerology_reduce($sum);
    return $sum;
}

function numerology_chakra_key($n) {
    $map = array(
        0  => 'Soul in Purest Form',
        1  => 'Root',
        2  => 'Sacral',
        3  => 'Solar Plexus',
        4  => 'Heart',
        5  => 'Throat',
        6  => 'Third Eye',
        7  => 'Crown',
        8  => 'Soul Star',
        9  => 'Earth Star',
        11 => 'Master 11',
        22 => 'Master 22',
        33 => 'Master 33',
        44 => 'Master 44',
        55 => 'Master 55',
        66 => 'Master 66',
        77 => 'Master 77',
        88 => 'Master 88',
        99 => 'Master 99',
    );
    return isset($map[intval($n)]) ? $map[intval($n)] : '';
}

function numerology_sum_all($str) {
    $vals = _num_letter_values();
    $upper = strtoupper(preg_replace('/[^A-Za-z]/', '', $str));
    $sum = 0;
    for ($i = 0; $i < strlen($upper); $i++) {
        if (isset($vals[$upper[$i]])) $sum += $vals[$upper[$i]];
    }
    return $sum;
}

function numerology_sum_vowels_only($str) {
    $vals = _num_letter_values();
    $vowels = _num_vowels();
    $upper = strtoupper(preg_replace('/[^A-Za-z]/', '', $str));
    $sum = 0;
    for ($i = 0; $i < strlen($upper); $i++) {
        if (in_array($upper[$i], $vowels) && isset($vals[$upper[$i]])) {
            $sum += $vals[$upper[$i]];
        }
    }
    return $sum;
}

function numerology_sum_consonants_only($str) {
    $vals = _num_letter_values();
    $vowels = _num_vowels();
    $upper = strtoupper(preg_replace('/[^A-Za-z]/', '', $str));
    $sum = 0;
    for ($i = 0; $i < strlen($upper); $i++) {
        if (!in_array($upper[$i], $vowels) && isset($vals[$upper[$i]])) {
            $sum += $vals[$upper[$i]];
        }
    }
    return $sum;
}

function run_numerology_calculation($full_name, $day, $month, $year) {
    // Name Number — all letters summed
    $name_raw     = numerology_sum_all($full_name);
    $name_reduced = numerology_reduce($name_raw);

    // Soul Urge — vowels only
    $soul_raw     = numerology_sum_vowels_only($full_name);
    $soul_reduced = numerology_reduce($soul_raw);

    // Personality — consonants only
    $pers_raw     = numerology_sum_consonants_only($full_name);
    $pers_reduced = numerology_reduce($pers_raw);

    // Life Path — sum all individual digits of day+month+year concatenated
    $lp_str = (string)intval($day) . (string)intval($month) . (string)intval($year);
    $lp_raw = 0;
    foreach (str_split($lp_str) as $d) $lp_raw += intval($d);
    $lp_reduced = numerology_reduce($lp_raw);

    // Birthday — day only
    $bday_raw     = intval($day);
    $bday_reduced = numerology_reduce($bday_raw);

    // Maturity — life path reduced + name number reduced
    $mat_raw     = $lp_reduced + $name_reduced;
    $mat_reduced = numerology_reduce($mat_raw);

    // Personal Year — day + month + current year digits summed
    $current_year = intval(date('Y'));
    $py_str = (string)intval($day) . (string)intval($month) . (string)$current_year;
    $py_raw = 0;
    foreach (str_split($py_str) as $d) $py_raw += intval($d);
    $py_reduced = numerology_reduce($py_raw);

    // Karmic Debts — check raw name, life path, birthday
    $karmic = array();
    foreach (array($name_raw, $lp_raw, $bday_raw) as $n) {
        if (numerology_is_karmic($n)) $karmic[] = $n;
    }
    $karmic = array_values(array_unique($karmic));

    return array(
        'full_name'     => $full_name,
        'name_number'   => array('raw' => $name_raw,  'reduced' => $name_reduced,  'chakra' => numerology_chakra_key($name_reduced)),
        'soul_urge'     => array('raw' => $soul_raw,   'reduced' => $soul_reduced,   'chakra' => numerology_chakra_key($soul_reduced)),
        'personality'   => array('raw' => $pers_raw,   'reduced' => $pers_reduced,   'chakra' => numerology_chakra_key($pers_reduced)),
        'life_path'     => array('raw' => $lp_raw,     'reduced' => $lp_reduced,     'chakra' => numerology_chakra_key($lp_reduced)),
        'birthday'      => array('raw' => $bday_raw,   'reduced' => $bday_reduced,   'chakra' => numerology_chakra_key($bday_reduced)),
        'maturity'      => array('raw' => $mat_raw,    'reduced' => $mat_reduced,    'chakra' => numerology_chakra_key($mat_reduced)),
        'personal_year' => array('raw' => $py_raw,     'reduced' => $py_reduced,     'chakra' => numerology_chakra_key($py_reduced)),
        'karmic_debts'  => $karmic,
    );
}
